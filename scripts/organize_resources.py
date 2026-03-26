import os
import requests
import json
from pathlib import Path

# Expanded data including all branches from branchSyllabusMap
BRANCH_SYLLABUS_MAP = {
    'CSE': {
        1: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_I-YEAR_2.pdf',
        2: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_I-YEAR_2.pdf',
        3: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_II-YEAR_3.pdf',
        4: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_II-YEAR_3.pdf',
        5: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_III-YEAR_2.pdf',
        6: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_III-YEAR_2.pdf',
        7: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_IV-YEAR_2.pdf',
        8: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22_CSE_IV-YEAR_2.pdf',
    },
    'CSM': {
        1: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-I-YEAR-CSM-1.pdf',
        2: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-I-YEAR-CSM-1.pdf',
        3: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-II-YEAR-CSM-1.pdf',
        4: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-II-YEAR-CSM-1.pdf',
        5: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-III-YEAR-CSM-1.pdf',
        6: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-III-YEAR-CSM-1.pdf',
        7: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IV-YEAR-CSM-1.pdf',
        8: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IV-YEAR-CSM-1.pdf',
    },
    'CSD': {
        1: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/CSD-R22-I.pdf',
        2: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/CSD-R22-I.pdf',
        3: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/CSD_II_YEAR_R22_IV-1_min.pdf',
        4: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/CSD_II_YEAR_R22_IV-1_min.pdf',
        5: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/CSD-III-YEAR-R22_VI-1_min.pdf',
        6: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/CSD-III-YEAR-R22_VI-1_min.pdf',
        7: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IV-CSD-YEAR-SYLLABUS.pdf',
        8: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IV-CSD-YEAR-SYLLABUS.pdf',
    },
    'IT': {
        1: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/it-r18-1.pdf',
        2: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/it-r18-1.pdf',
        3: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/it-r18-2.pdf',
        4: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/it-r18-2.pdf',
        5: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IT-III-YEAR.pdf',
        6: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IT-III-YEAR.pdf',
        7: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IT-IV-YEAR.pdf',
        8: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-IT-IV-YEAR.pdf',
    },
    'ECE': {
        1: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ece-r18-1.pdf',
        2: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ece-r18-1.pdf',
        3: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ece-r18-2.pdf',
        4: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ece-r18-2.pdf',
        5: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-ECE-III-YEAR-SYLLABUS.pdf',
        6: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-ECE-III-YEAR-SYLLABUS.pdf',
        7: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-ECE-IV-YEAR-SLLABUS.pdf',
        8: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-ECE-IV-YEAR-SLLABUS.pdf',
    },
    'EEE': {
        1: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/eee-r18-1.pdf',
        2: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/eee-r18-1.pdf',
        3: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/II-EEE-R18.pdf',
        4: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/II-EEE-R18.pdf',
        5: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-EEE-III-YEAR-R1.pdf',
        6: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-EEE-III-YEAR-R1.pdf',
        7: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-EEE-IV-YEAR-R1.pdf',
        8: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-EEE-IV-YEAR-R1.pdf',
    },
    'CIVIL': {
        1: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ce-r18-1.pdf',
        2: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ce-r18-1.pdf',
        3: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ce-r18-2.pdf',
        4: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/ce-r18-2.pdf',
        5: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-CIVIL-III-YEAR-SYLLABUS.pdf',
        6: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-CIVIL-III-YEAR-SYLLABUS.pdf',
        7: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-CIVIL-IV-YEAR-SYLLABUS-1.pdf',
        8: 'https://tkrcet.ac.in/wp-content/uploads/2025/07/R22-CIVIL-IV-YEAR-SYLLABUS-1.pdf',
    },
}

QUESTION_PAPERS_BASE = "https://tkrcetexams.com/Question_Papers/22Batch/"
PAPERS_MAP = {
    "semester_1": ["4E1AD.pdf", "1E1AK.pdf", "4E1DD.pdf", "1E1AE.pdf", "3E1AD.pdf"],
    "semester_2": ["2E2AF.pdf", "3E2AG.pdf", "4E2BA.pdf"],
    "semester_3": ["2E3AB.pdf", "3E3AC.pdf", "4E3AD.pdf", "5E3AE.pdf"],
    "semester_4": ["2E4BA.pdf", "3E4BB.pdf", "4E4BC.pdf", "5E4BD.pdf"],
    "semester_5": ["3.1EQP/2E5AA.pdf", "3.1EQP/3E5AB.pdf", "3.1EQP/4E5AC.pdf", "3.1EQP/5E5AD.pdf"], # Added subfolder prefix if needed
    "semester_6": ["3-2%20QP/2P5EE.pdf", "3-2%20QP/A3H5DA.pdf", "3-2%20QP/2E5CB.pdf", "3-2%20QP/3P5HE.pdf", "3-2%20QP/3E5DA.pdf"],
    "semester_7": ["4.1EQP/3O7EB.pdf", "4.1EQP/4E7AB.pdf", "4.1EQP/5E7AC.pdf", "4.1EQP/6E7AD.pdf"],
}

BASE_DIR = Path(__file__).parent.parent / "frontend" / "assets" / "resources"

def download_file(url, dest_folder):
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        
        filename = os.path.basename(requests.utils.unquote(url))
        filepath = dest_folder / filename
        
        if filepath.exists():
            return True
            
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filename} to {dest_folder.name}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    print("Starting comprehensive resource organization...")
    
    # 1. Download Syllabus for all branches
    for branch, sem_map in BRANCH_SYLLABUS_MAP.items():
        print(f"\nProcessing Branch: {branch} Syllabi...")
        for sem, url in sem_map.items():
            sem_dir = BASE_DIR / "R22" / f"semester_{sem}" / "syllabus"
            sem_dir.mkdir(parents=True, exist_ok=True)
            download_file(url, sem_dir)
            
    # 2. Download Question Papers
    print("\nProcessing Question Papers...")
    for sem_name, files in PAPERS_MAP.items():
        dest_folder = BASE_DIR / "R22" / sem_name / "papers"
        dest_folder.mkdir(parents=True, exist_ok=True)
        for f in files:
            # Handle possible nested paths in PAPERS_MAP
            url_part = f
            if "/" in f:
                filename = f.split("/")[-1]
            else:
                # Need to map semester_X back to formal portal folder names if not specified
                folder_map = {
                    "semester_1": "1.1EQP/",
                    "semester_2": "1.2EQP/",
                    "semester_3": "2.1EQP/",
                    "semester_4": "2.2EQP/",
                }
                url_part = folder_map.get(sem_name, "") + f
            
            url = QUESTION_PAPERS_BASE + url_part
            download_file(url, dest_folder)
            
    print("\nComprehensive resource organization complete.")

if __name__ == "__main__":
    main()
