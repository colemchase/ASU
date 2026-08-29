# Coverage Screenshot Instructions

Run the Java test harness:

```bash
javac -cp ".:lib/*" VendingMachine.java VendingMachineTestHarness.java
java -javaagent:lib/jacocoagent.jar -cp ".:lib/*" VendingMachineTestHarness
```

Capture the terminal output that shows:

- each passing assertion
- the `VendingMachine.java` lines covered by each test
- total line coverage
- total decision coverage

Save the screenshot here:

```text
screenshots/coverage.png
```

The LaTeX report already looks for that exact file. After adding the screenshot, rebuild the PDF:

```bash
pdflatex -interaction=nonstopmode Coleman_Chase_CSE565_Structural-Based_Testing_Project.tex
pdflatex -interaction=nonstopmode Coleman_Chase_CSE565_Structural-Based_Testing_Project.tex
cp Coleman_Chase_CSE565_Structural-Based_Testing_Project.pdf "Coleman_Chase_CSE 565_Structural-Based Testing Project.pdf"
```
