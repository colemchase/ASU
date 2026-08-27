# Specification-Based Testing Defect Candidates

These are failed test executions found by running the command-line JAR. Each case uses the required argument order:

```text
Name Age UserStatus RewardStatus Season ProductCategory Rating
```

## D1 - New User Incorrectly Receives Discount

- Test case: Test Case #24
- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 New Gold Summer Electronics 5
```

- Expected: No discount, because new users cannot receive discounts.
- Actual: `The discount given is 10%`
- Requirement mapping: `9.1`

## D2 - Username Longer Than 10 Characters Is Accepted

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Christopher 24 Returning Gold Summer Electronics 5
```

- Expected: Username length error.
- Actual: `The discount given is 15%`
- Requirement mapping: `1.1`

## D3 - Username With Underscore Is Accepted

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter_J 24 Returning Gold Summer Electronics 5
```

- Expected: Username underscore error.
- Actual: `The discount given is 15%`
- Requirement mapping: `1.3`

## D4 - Age 17 Is Accepted

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 17 Returning Gold Summer Electronics 5
```

- Expected: Age error because age must be 18 or older.
- Actual: `The discount given is 15%`
- Requirement mapping: `2.1`

## D5 - Rating 0 Is Accepted

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 Returning Gold Summer Electronics 0
```

- Expected: Rating error because rating must be between 1 and 10.
- Actual: `The discount given is 15%`
- Requirement mapping: `7.1`

## D6 - Negative Rating Is Accepted

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 Returning Gold Summer Electronics -1
```

- Expected: Rating error because rating must be between 1 and 10.
- Actual: `The discount given is 15%`
- Requirement mapping: `7.1`

## D7 - Spring Bronze Electronics Discount Is Too Low

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 Returning Bronze Spring Electronics 5
```

- Expected: `The discount given is 10%`
- Actual: `The discount given is 5%`
- Requirement mapping: `9.4.1`

## D8 - Winter Gold Electronics Discount Is Too Low

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 Returning Gold Winter Electronics 5
```

- Expected: `The discount given is 25%`
- Actual: `The discount given is 20%`
- Requirement mapping: `9.5.1`

## D9 - Fall Silver Electronics Discount Is Too Low

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 Returning Silver Fall Electronics 5
```

- Expected: `The discount given is 15%`
- Actual: `The discount given is 10%`
- Requirement mapping: `9.6.1`

## D10 - Unknown Product Incorrectly Receives Discount

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 Returning Silver Summer Unknown 5
```

- Expected: No discount because product category is unknown.
- Actual: `The discount given is 10%`
- Requirement mapping: `9.2`

## Extra Candidate - Returning Gold Fall Electronics Incorrectly Receives Discount

- Command:

```bash
java -jar "extracted/Jar Files and Project1Script/CSE565P1.jar" Peter 24 Returning Gold Fall Electronics 5
```

- Expected: No discount because this combination is not one of the specified discount cases.
- Actual: `The discount given is 10%`
- Requirement mapping: `9.7`
