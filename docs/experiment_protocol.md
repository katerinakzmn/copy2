# Experiment Protocol: Real-LLM Evaluation of Escalation Policies

## 1. Research question

Which escalation policy provides the best cost-quality trade-off for function- and module-level Python bug-fixing tasks when using real LLMs with two capability tiers?

## 2. Scope

This study evaluates escalation decisions in a controlled benchmark environment. It does not claim to measure all software-engineering tasks or the general coding ability of a particular model.

The benchmark dataset contains original or derived-and-validated Python bug-fixing tasks. Each task has buggy code, a task description, unit tests, a validated reference solution, and metadata from a predefined taxonomy.

## 3. Model tiers

- Weak tier: a GPT-4-class OpenAI model; the exact API model identifier is recorded in each experiment manifest.
- Strong tier: GPT-5; the exact API model identifier is recorded in each experiment manifest.
- Human tier: a simulated reliable fallback for mock/unit-test scenarios. It is reported separately and is not interpreted as evidence of real human performance.

## 4. Policies

Primary real-LLM policies:
- FixedWeak
- FixedStrong
- RetryThenEscalate
- ConfidenceThreshold
- ProgressHeuristic

Supplementary policies:
- HumanFallback, evaluated only as a clearly labelled hypothetical fallback scenario.
- Random, used as a stochastic baseline.
- Oracle, used only for mock-based validation; it is not a real-LLM upper bound.

## 5. Controlled conditions

All policies use the same task description, initial buggy code, system prompt, test-feedback format, maximum number of attempts, output-token limit, timeout rules, and API-error handling rules.

The initial experimental configuration is:

```yaml
temperature: 0
max_attempts_per_episode: 3
max_output_tokens: 600
pilot_tasks: 20
main_tasks: 120
main_repetitions: 2
```

No reference solution, oracle label, hidden-test content, or internal task-construction metadata is included in an LLM prompt.

## 6. Dataset construction

The dataset is constructed according to a predefined taxonomy covering defect type, task domain, difficulty, code scope, reasoning requirement, feedback type, and context size.

Tasks are created as original templates or as documented derived tasks using controlled bug mutations. The benchmark does not claim exhaustive coverage of all software-engineering tasks. It provides systematic, stratified coverage of selected dimensions that are relevant to escalation decisions.

Each task must satisfy all of the following conditions:

1. The buggy implementation fails at least one test.
2. The reference implementation passes all tests.
3. Required task metadata is present.
4. The task identifier is unique.
5. The task is not a near-duplicate of another task in the same evaluation split.

## 7. Primary metrics

- Solve rate.
- Average and median actual API cost in USD.
- Average input, cached-input, and output tokens.
- Average number of attempts.
- Strong-escalation rate.
- Human-fallback rate, when applicable.
- Wall-clock latency.
- Failure-type distribution.

## 8. Definition of preferred policy

The preferred policy is the policy with the lowest mean actual API cost among policies whose solve rate is within 2 percentage points of the highest observed solve rate.

If no policy satisfies this criterion robustly, results are reported as an observed cost-quality trade-off rather than as a single winner.

## 9. Repetitions and uncertainty

Each task-policy combination is executed twice in the main experiment. Additional repetitions are run for close or unstable comparisons. Results report the number of episodes and 95% bootstrap confidence intervals for solve rate and mean cost where feasible.

## 10. Budget and stopping rules

The pilot is run before the main experiment to estimate cost per task. The main budget is fixed only after pilot results are reviewed.

Each episode has a maximum number of model attempts, a maximum output-token limit, and a maximum USD cost. API failures are logged as API errors and are not silently retried beyond the specified handling rules.

## 11. Reproducibility

Each run saves the git commit hash, timestamp, task dataset version, prompt version, model identifiers, pricing snapshot, random seed, per-step token usage, per-step cost, per-task outcomes, and aggregate metrics.
