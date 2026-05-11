"""
run_all.py
==========
Execute the full pipeline. Run individual steps with:
    python run_all.py 1 2 3
or all steps:
    python run_all.py
"""
import sys
from pipeline import step1, step2, step3, step4, step5, step6, step7, step8

STEPS = {1: step1, 2: step2, 3: step3, 4: step4,
         5: step5, 6: step6, 7: step7, 8: step8}


def main():
    if len(sys.argv) > 1:
        chosen = [int(s) for s in sys.argv[1:]]
    else:
        chosen = list(STEPS.keys())
    for s in chosen:
        STEPS[s]()
    print("\nAll requested steps completed.")


if __name__ == "__main__":
    main()
