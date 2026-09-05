# Task Construction and Validation Rules

## 1. Goal

This document defines how original benchmark instances are created and validated. The aim is to construct a reproducible, systematic task set for evaluating escalation policies rather than to claim exhaustive coverage of all programming tasks.

## 2. Construction workflow

1. Create a small validated reference implementation for a function, class, or module.
2. Write a concise task description and unit tests representing its expected behavior.
3. Create a buggy variant using one documented mutation operator from the taxonomy.
4. Confirm that the buggy variant fails at least one test.
5. Confirm that the reference implementation passes all tests.
6. Add metadata: task ID, domain, dominant defect type, mutation operator, difficulty, code scope, reasoning requirement, feedback type, context size, and construction method.
7. Run the dataset validation script before adding the task to the final split.

## 3. Controlled mutation examples

- Boundary error: replace an inclusive comparison with an exclusive one.
- Conditional error: reverse a predicate or return from the wrong branch.
- Transformation error: use an incorrect filter, sort key, aggregation, or mapping.
- State error: omit an invalidation/update step or mutate the input unexpectedly.
- Invalid-input error: remove validation for empty values, missing keys, or unsupported types.
- Exception error: catch the wrong exception, suppress an exception, or omit required handling.
- Parsing error: use an incorrect delimiter, date format, or serialization field.
- Algorithmic error: use a wrong stopping condition, traversal rule, or update invariant.
- Contract error: return the wrong type, preserve a wrong default, or violate the documented API.
- Resource/time error: introduce non-termination, avoidable repeated work, or missing cleanup.

## 4. Independence and duplicate control

Tasks must not differ only by variable names, numeric literals, or superficial wording. Tasks derived from the same template must have different dominant mutation operators and, where possible, different reasoning requirements or feedback patterns.

## 5. Required metadata example

```json
{
  "task_id": "B3_MED_014",
  "domain": "collections",
  "defect_type": "B3_data_transformation",
  "mutation_operator": "incorrect_sort_key",
  "difficulty": "medium",
  "code_scope": "single_function",
  "reasoning_requirement": "multi_step_logic",
  "feedback_type": "failing_unit_test",
  "context_size": "short",
  "construction_method": "controlled_mutation",
  "reference_validated": true,
  "buggy_code_fails": true
}
```

## 6. Validation invariants

A task can enter the benchmark only if:

- the reference solution passes all tests;
- the buggy implementation fails at least one test;
- the task ID is unique;
- all required metadata fields are present;
- the task does not exceed the declared context-size category by a large margin;
- the prompt does not include the reference solution, oracle label, hidden-test text, or construction notes.

## 7. Attribution and academic integrity

The benchmark dataset is built from original task templates and controlled mutations. If any external code or example is used as inspiration or source material, its license and attribution are recorded in the task manifest. External benchmarks may be cited as related work or used only as clearly labelled external validation sets; their tasks are not represented as original benchmark tasks.
