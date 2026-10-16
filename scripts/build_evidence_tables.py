"""Export supplementary LaTeX tables from existing Research result summaries.

No experiment is run. Research owns the input results; these are paper exports.
Usage: python scripts/build_evidence_tables.py --research-root C:/workspace/se3-wam-research
"""
from pathlib import Path
import argparse
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
ARMS = ["P00","P01","P02","P03","P04","P05","P06","P07","P08","P09","Aalpha","P12","P13","P14","P15"]
TARGETS = [
"None", "3-D scene flow", "Target pose", "Scene flow + pose",
"Wan latent + pose", "Dense 2-D displacement + pose", "Codec motion + pose",
"Sparse scene tracks + pose", "Scene flow + object DINO", "Scene flow + target tracks",
"P03 + motion magnitude", "P03 + depth", "P03 + DINO", "P03 + dynamic RGB",
"P03 + depth/DINO/dynamic RGB"]
TASKS = ["grasp","t1_belt","t1_occ","t1_so3","t1_xyz","t2_se3","t2_trans","t3_full","t3_phase","t4_can","t4_slider","t4_sphere","t4_sphere_tabletop","t5_replan"]
SHORT = ["G","B","O","R","X","S","T","F","P","C","L","H","HT","I"]
def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
def tex(value):
    return str(value).replace("_", r"\_")
def table(name, caption, label, spec, headers, rows, wide=True):
    env = "table*" if wide else "table"
    lines = ["% Generated from Research source summaries; do not edit numerical cells.",
             rf"\begin{{{env}}}[t]", r"\centering\small",
             r"\caption{" + caption + "}", r"\label{" + label + "}",
             r"\begin{tabular}{@{}" + spec + "@{}}", r"\toprule",
             " & ".join(headers) + r" \\", r"\midrule"]
    lines += [" & ".join(str(x) for x in row) + r" \\" for row in rows]
    lines += [r"\bottomrule",r"\end{tabular}",rf"\end{{{env}}}",""]
    (ROOT/"tables"/name).write_text("\n".join(lines),encoding="utf-8")
def main(research):
    src=research/"docs/experiments/FUTURE0/results/independent1260/analysis"
    summary={r["arm"]:r for r in read_csv(src/"arm-summary.csv")}
    fixed={r["arm"]:r for r in read_csv(src/"fixed140-arm-summary.csv")}
    if set(summary) != set(ARMS):
        raise ValueError("Unexpected FUTURE0 arm set")
    rows=[]
    for arm,target in zip(ARMS,TARGETS):
        r=summary[arm]
        if int(r["n"])!=1260:
            raise ValueError("Unexpected evaluation denominator")
        rows.append([arm,target,fixed[arm]["successes"],r["successes"],
                     f'{100*int(r["successes"])/1260:.2f}'])
    table("future_complete.tex",
          "All future-supervision conditions: one training seed, four epochs, common privileged object-motion input, and action-only deployment. Development counts and the disjoint complement are kept separate.",
          "tab:all_future","llrrr",["ID","Future supervision","/140","/1,260","SR (\\%)"],rows)
    pairs={(r["arm"],r["reference_arm"]):r for r in read_csv(src/"paired-summary.csv") if r["scope"]=="overall"}
    rows=[]
    for arm in ARMS:
        if arm=="P00":
            continue
        row=[arm]
        for ref in ["P00","P03"]:
            if arm == ref:
                row += ["---","---"]
            else:
                r=pairs[(arm,ref)]
                row += [r["arm_only_success"]+"/"+r["reference_only_success"],
                        f'{float(r["mcnemar_exact_two_sided_p"]):.6f}']
        rows.append(row)
    table("future_paired.tex",
          "Overall paired gains/losses and raw two-sided exact McNemar probabilities. Columns compare each candidate to P00 or P03 over 1,260 scenes. The twenty-seven available contrasts form the reported Bonferroni family; P03 against itself is inapplicable.",
          "tab:paired_future","lrrrr",
          ["ID","Gain/loss vs P00","Raw $p$","Gain/loss vs P03","Raw $p$"],rows)
    counts={(r["arm"],r["task_id"]):int(r["successes"]) for r in read_csv(src/"task-summary.csv")}
    rows=[]
    for arm in ARMS:
        values=[counts[(arm,task)] for task in TASKS]
        if sum(values)!=int(summary[arm]["successes"]):
            raise ValueError("Per-task and overall counts disagree")
        rows.append([arm]+values+[sum(values)])
    task_key="Task abbreviations: G=grasp, B=belt, O=occlusion, R=SO3, X=XYZ, S=T2 SE3, T=T2 translation, F=T3 full, P=T3 phase, C=can, L=slider, H=sphere, HT=tabletop sphere, I=impact/replan."
    table("future_tasks.tex",
          "Full future-study success counts, ninety episodes per task per condition. Every task is retained, including zero-success tasks. "+task_key,
          "tab:future_tasks","l"+"r"*15,["ID"]+SHORT+["Total"],rows)
    failure={(r["arm"],r["category"]):int(r["count"]) for r in read_csv(src/"failure-summary.csv") if r["scope"]=="overall" and r["field"]=="failure_class"}
    cats=["boundary","safety","task_violation","timeout"]
    rows=[]
    for arm in ARMS:
        values=[failure[(arm,c)] for c in cats]
        if sum(values)!=int(summary[arm]["failures"]):
            raise ValueError("Failure categories do not cover failures")
        rows.append([arm]+values+[sum(values)])
    table("future_failures.tex",
          "Native evaluator failure categories out of 1,260 episodes per condition. Safety is the evaluator category, not a certified safety measure. All failures stay in the score denominator.",
          "tab:future_failures","lrrrrr",["ID","Boundary","Safety","Task violation","Timeout","All failures"],rows)
    d=json.loads((research/"docs/experiments/BASE2/results/candidate-comparison.json").read_text(encoding="utf-8"))
    if not d["accepted"] or d["n_per_arm"]!=1400:
        raise ValueError("Unexpected BASE2 result scope")
    combo_arms=["A","B","C","D","G","H","I","J","K","L","M","N"]
    rows=[]
    for task in TASKS:
        rows.append([tex(task)]+[d["per_task"][task][arm]["successes"] for arm in combo_arms])
    totals={r["arm"]:r["successes"] for r in d["ranking"]}
    rows.append(["Total"]+[totals[a] for a in combo_arms])
    table("combination_tasks.tex",
          "All combination-study task counts, one hundred episodes per task, including development scenes. A/B=P15 DINO-S reconstruction on/off; C/D=P15 CNN on/off; G/H=P07 DINO-S on/off; I/J=P07 CNN on/off; K/L=P09 DINO-S on/off; M/N=P09 CNN on/off. All twelve conditions have one training seed.",
          "tab:combination_tasks","l"+"r"*12,["Task"]+combo_arms,rows)
    print("Exported five supplementary tables; counts and denominators checked.")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--research-root",type=Path,required=True)
    main(parser.parse_args().research_root)
