import os
import csv

def read_expected_verbs(csv_path):
    """
    Reads the CSV file and extracts the list of expected verbs.
    
    Args:
        csv_path (str): Path to the CSV file.
    
    Returns:
        set: A set of expected verb names (without .mp3 extension).
    """
    expected_verbs = set()
    try:
        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                verb = row.get('verb')
                if verb:
                    expected_verbs.add(verb.strip())
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_path}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit(1)
    return expected_verbs

def get_existing_mp3_files(milim_dir):
    """
    Traverses the milim directory and its subdirectories to find all .mp3 files.
    
    Args:
        milim_dir (str): Path to the milim directory.
    
    Returns:
        set: A set of existing mp3 filenames (with .mp3 extension).
    """
    existing_mp3s = set()
    for root, dirs, files in os.walk(milim_dir):
        for file in files:
            if file.lower().endswith('.mp3'):
                # Store filenames with exact casing
                existing_mp3s.add(file)
    return existing_mp3s

def find_missing_mp3s(expected_verbs, existing_mp3s):
    """
    Identifies which expected mp3 files are missing.
    
    Args:
        expected_verbs (set): Set of expected verb names.
        existing_mp3s (set): Set of existing mp3 filenames.
    
    Returns:
        list: List of missing mp3 filenames.
    """
    missing_mp3s = []
    for verb in expected_verbs:
        mp3_filename = f"{verb}.mp3"
        if mp3_filename not in existing_mp3s:
            missing_mp3s.append(mp3_filename)
    return missing_mp3s

def main():
    # Define paths
    root_dir = os.getcwd()
    csv_filename = 'verb_binyan.csv'
    csv_path = os.path.join(root_dir, csv_filename)
    milim_dir = os.path.join(root_dir, 'milim')
    
    # Check if milim directory exists
    if not os.path.isdir(milim_dir):
        print(f"Error: Directory '{milim_dir}' does not exist.")
        exit(1)
    
    # Read expected verbs from CSV
    expected_verbs = read_expected_verbs(csv_path)
    if not expected_verbs:
        print("No verbs found in the CSV file.")
        exit(0)
    
    # Get existing mp3 files
    existing_mp3s = get_existing_mp3_files(milim_dir)
    
    # Find missing mp3s
    missing_mp3s = find_missing_mp3s(expected_verbs, existing_mp3s)
    
    # Output results
    if missing_mp3s:
        print("Missing .mp3 files:")
        for mp3 in missing_mp3s:
            print(mp3)
    else:
        print("All expected .mp3 files are present.")

if __name__ == "__main__":
    main()
