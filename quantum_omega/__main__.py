from .core import Action, Claim, Ledger, Stage, select_action

def main():
    ledger = Ledger()
    ledger.register(Claim("demo-001", "Illustrative hypothesis, not a verified physical claim", ("local:demo",)))
    ledger.advance("demo-001", Stage.CONJECTURE, "local:assumptions.md", "reviewer-a", "author-a")
    selected = select_action([
        Action("derive a falsifiable prediction", 3, 2, 2, 3, 2, 1),
        Action("repeat an uninformative simulation", 0.1, 0, 0.1, 0.1, 2, 1),
    ])
    print("Illustrative next action:", selected.name)
    print("Audit events:", len(ledger.events))
    print("No scientific discovery or empirical validation is asserted.")

if __name__ == "__main__":
    main()
