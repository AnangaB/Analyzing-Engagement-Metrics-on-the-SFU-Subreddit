import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn

seaborn.set()


def main(input_keyword_data_root, column_name, output_plot_filename):
    keyword_data = pd.read_csv(
        os.path.join(input_keyword_data_root, f"{column}_transformed.csv"),
        index_col="keyword",
    )
    keywords_to_plot = pd.read_csv(
        os.path.join(input_keyword_data_root, f"to_plot.csv"),
        index_col="keyword",
    )

    if len(keywords_to_plot.index) == 0:
        keywords_data_to_plot = keyword_data
    else:
        keywords_data_to_plot = keyword_data.merge(keywords_to_plot, on="keyword")
    keywords_data_to_plot = keywords_data_to_plot.reset_index()

    keywords_data_to_plot = keywords_data_to_plot[keywords_data_to_plot['pvalue_significant_bonferri'] == True]

    # print(keywords_data_to_plot)

    def create_keyword_label(row):
        # The '{:.2e}' is to make format be in scientific notation with 2
        # decimal places after the period. I learned how to do this formatting
        # from: "https://stackoverflow.com/questions/34032855/rounding-scientific-notation-in-python"
        return f"{row['keyword']}\n{'{:0.2e}'.format(row['pvalue'])}"

    keywords_labels_to_plot = keywords_data_to_plot.apply(
        create_keyword_label, axis=1
    )
    keyword_labels = list(keywords_labels_to_plot)

    # Plotting code adapter from: "https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html"

    fig, ax = plt.subplots(layout="constrained")

    width = 0.25
    multiplier = 0
    x = np.arange(len(keywords_data_to_plot.index))

    for partition_data in (
        ("With Keyword", f"avg_{column_name}_with"),
        ("Without Keyword", f"avg_{column_name}_without"),
    ):
        partition_name = partition_data[0]
        partition_column = partition_data[1]
        heights = list(keywords_data_to_plot[partition_column])
        heights = list(map(lambda x: round(x, 2), heights))

        offset = width * multiplier
        rects = ax.bar(x + offset, heights, width, label=partition_name)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel(f"Average {column_name.replace('_', ' ').title()}")
    ax.set_xlabel(f"Keyword")
    title = f"Average Submission {column_name.replace('_', ' ').title()} With and Without"
    if len(keyword_labels) == 1:
        title += f" Keyword {keyword_labels[0]}"
        ax.set_ylim(
            0,
            max(
                keywords_data_to_plot[f"avg_{column_name}_with"].max(),
                keywords_data_to_plot[f"avg_{column_name}_without"].max(),
            )
            * 2,
        )
    else:
        title += " Keywords"
    ax.set_title(title)
    ax.set_xticks(x + width / 2, keyword_labels)
    ax.legend(ncols=2)

    # Use set_size_inches to make plot big enough to fit all labels without a
    # bunch of overlap.
    fig.set_size_inches(15, 5)
    plt.savefig(output_plot_filename)


if __name__ == "__main__":
    keywords_data_root = sys.argv[1]
    keywords_type = sys.argv[2]
    column = sys.argv[3]
    output_filename = sys.argv[4]
    main(
        os.path.join(keywords_data_root, keywords_type),
        column,
        output_filename,
    )
