# Task Taxonomy and Coverage Plan

## Purpose

The task taxonomy was designed specifically for evaluation of escalation policies. It does not claim to enumerate every possible software-engineering problem. Instead, it defines dimensions whose combinations can make retry, escalation, or stopping decisions meaningfully different.

## Primary defect types

| ID | Defect type | Examples |
|---|---|---|
| B1 | Boundary and off-by-one errors | Empty input, first/last element, range endpoint, index shift |
| B2 | Incorrect conditional logic | Reversed predicate, wrong branch, premature return |
| B3 | Data transformation errors | Incorrect filtering, mapping, aggregation, sort order |
| B4 | State and mutation errors | Unintended input mutation, stale cache, incorrect state update |
| B5 | Invalid-input handling | `None`, empty values, missing keys, wrong types, invalid defaults |
| B6 | Exception handling errors | Missing `try/except`, swallowed exception, wrong exception type |
| B7 | Parsing and serialization errors | JSON, text parsing, date formats, serialization contracts |
| B8 | Algorithmic logic errors | Traversal, termination, search, graph logic, dynamic programming |
| B9 | API and contract violations | Wrong return type, wrong signature, incorrect default behavior |
| B10 | Resource and time behavior | Infinite loop, avoidable timeout, resource cleanup, inefficient path |

## Additional task dimensions

| Dimension | Values |
|---|---|
| Difficulty | easy, medium, hard |
| Code scope | single_function, multi_function, class_or_module |
| Reasoning requirement | local_edit, multi_step_logic, stateful_reasoning, algorithmic_reasoning, specification_interpretation |
| Feedback type | failing_unit_test, exception_traceback, multiple_failures, partial_pass_rate |
| Context size | short, medium, long |
| Domain | strings, collections, algorithms, data_structures, validation, parsing, dates_numbers, file_json_io |
| Construction method | original_template, controlled_mutation, manually_validated_derived_task |

## Target coverage: 120 tasks

| Difficulty | Target tasks | Intended role |
|---|---:|---|
| Easy | 40 | Tests whether early weak-tier attempts are sufficient and whether escalation is wasteful |
| Medium | 40 | Tests the central retry-versus-escalate decision |
| Hard | 40 | Tests whether policies escalate in time and control failure cost |
| Total | 120 | Supports aggregate and stratified analysis |

## Target domain allocation

| Domain | Target tasks |
|---|---:|
| Strings and text processing | 16 |
| Collections: lists, arrays, dictionaries | 20 |
| Algorithms and search | 18 |
| Data structures and state | 18 |
| Validation and exceptions | 14 |
| Parsing and serialization | 12 |
| Dates, numbers, and conversions | 10 |
| Files and JSON I/O | 12 |
| Total | 120 |

## Coverage principles

1. Every major domain contains easy, medium, and hard tasks where feasible.
2. A task is labelled by its dominant defect type and may contain secondary tags.
3. Variants of the same template must use materially different mutation operators; changing only a constant or identifier does not create an independent task.
4. The final benchmark manifest records the coverage matrix and any intentional deviations from target quotas.
