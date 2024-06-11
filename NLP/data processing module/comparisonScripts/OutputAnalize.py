import math
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def normalize_text(text):
    if isinstance(text, float) and math.isnan(text):
        return text

    text = text.lower()

    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove non-alphanumeric characters except whitespace

    text = re.sub(r'\s+', ' ', text).strip()

    return text


def preprocess_number_value(value):
    if isinstance(value, float) and math.isnan(value):
        return value

    if value in ['nan', '<()>', 'NA']:
        return np.nan

    if not isinstance(value, str):
        return np.nan

    numbers = []
    for num in value.strip('<>()').split(','):
        num = num.strip()
        if num:
            try:
                num = int(num)
                numbers.append(num)
            except ValueError:
                return np.nan

    if len(numbers) == 1:
        return numbers[0]

    return numbers


def compare_ages(processed_col, test_col):
    processed_normalized = processed_col.apply(preprocess_number_value)
    test_normalized = test_col.apply(preprocess_number_value)

    matches = ((processed_normalized == test_normalized) | (processed_normalized.isna() & test_normalized.isna())).sum()
    total = len(processed_col)

    accuracy = matches / total

    return accuracy


def compare_number_of_accidents_occured(processed_col, test_col):
    matches = (processed_col == test_col).sum()
    total = len(processed_col)
    return matches / total


def compare_day_of_the_week(processed_col, test_col):
    matches = (processed_col == test_col).sum()
    total = len(processed_col)
    return matches / total


def compare_normalize_text(processed_col, test_col):
    processed_normalized = processed_col.apply(normalize_text)
    test_normalized = test_col.apply(normalize_text)

    matches = ((processed_normalized == test_normalized) | (processed_normalized.isna() & test_normalized.isna())).sum()
    total = len(processed_col)

    accuracy = matches / total

    return accuracy


def compare_columns(processed_col, test_col, column):
    if len(processed_col) != len(test_col):
        raise ValueError("Columns must have the same length for comparison")

    comparison_functions = {
        "<number_of_accidents_occured>": compare_number_of_accidents_occured,
        "<day_of_the_week_of_the_accident>": compare_day_of_the_week,
        "<exact_location_of_accident>": compare_normalize_text,
        "<area_of_accident>": compare_normalize_text,
        "<division_of_accident>": compare_normalize_text,
        "<district_of_accident>": compare_normalize_text,
        "<subdistrict_or_upazila_of_accident>": compare_normalize_text,
        "<is_place_of_accident_highway_or_expressway_or_water_or_others>": compare_normalize_text,
        "<is_reason_or_cause_for_the_accident_ploughed_or_ram_or_hit_or_collision_or_breakfail_or_others>": compare_normalize_text,
        "<primary_vehicle_involved>": compare_normalize_text,
        "<secondary_vehicle_involved>": compare_normalize_text,
        "<tertiary_vehicle_involved>": compare_normalize_text,
        "<any_more_vehicles_involved>": compare_normalize_text,
        "<available_ages_of_the_deceased>": compare_ages,
    }

    def default_comparison(processed_col, test_col):
        matches = ((processed_col == test_col) | (pd.isna(processed_col) & pd.isna(test_col))).sum()
        total = len(processed_col)
        return matches / total

    compare_function = comparison_functions.get(column, default_comparison)
    return compare_function(processed_col, test_col)


def calculate_accuracy(output_file, columns_to_check):
    df = pd.read_csv("output_comparison.csv", sep=',')

    accuracy_results = {}

    for column in columns_to_check:
        processed_col_name = f"processed_{column}"
        test_col_name = f"test_{column}"

        if processed_col_name in df.columns and test_col_name in df.columns:
            processed_col = df[processed_col_name]
            test_col = df[test_col_name]

            accuracy = compare_columns(processed_col, test_col, column)
            accuracy_results[column] = accuracy

    return accuracy_results


if __name__ == "__main__":
    output_file = 'output_comparison.csv'
    columns_to_check = [
        "<number_of_accidents_occured>",
        "<is_the_accident_data_yearly_monthly_or_daily>",
        "<day_of_the_week_of_the_accident>",
        "<exact_location_of_accident>",
        "<area_of_accident>",
        "<division_of_accident>",
        "<district_of_accident>",
        "<subdistrict_or_upazila_of_accident>",
        "<is_place_of_accident_highway_or_expressway_or_water_or_others>",
        "<is_country_bangladesh_or_other_country>",
        "<is_type_of_accident_road_accident_or_train_accident_or_waterways_accident_or_plane_accident>",
        "<total_number_of_people_killed>",
        "<total_number_of_people_injured>",
        "<is_reason_or_cause_for_the_accident_ploughed_or_ram_or_hit_or_collision_or_breakfail_or_others>",
        "<primary_vehicle_involved>",
        "<secondary_vehicle_involved>",
        "<tertiary_vehicle_involved>",
        "<any_more_vehicles_involved>",
        "<available_ages_of_the_deceased>",
        "<accident_datetime_from_url>"
    ]

    accuracy_results = calculate_accuracy(output_file, columns_to_check)

    # Plotting
    columns = list(accuracy_results.keys())
    accuracies = [accuracy * 100 for accuracy in accuracy_results.values()]

    plt.figure(figsize=(20, 8))
    plt.barh(columns, accuracies, color='skyblue')
    plt.xlabel('Accuracy (%)')
    plt.title('Accuracy of Columns')
    plt.gca().invert_yaxis()
    plt.xlim(0, 100)
    for i, v in enumerate(accuracies):
        plt.text(v + 1, i, f'{v:.2f}%', va='center')
    plt.show()
    plt.savefig('accuracy_plot.png')
