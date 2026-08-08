# Project Learning Notes

This document records questions raised while building the project and the
answers learned from them. New questions should be appended under the most
relevant topic so the document becomes a reusable reference rather than a
chronological activity log.

## Python and testing

### Why are `first_results` and `second_results` tuples?

The smoke test creates the first result snapshot with:

```python
first_results = tuple(detector.detect(sample) for sample in samples)
```

The expression inside `tuple(...)` is a generator expression. It describes how
to produce results one at a time, but it does not execute all detector calls or
retain their outputs by itself. Passing it to `tuple` consumes the generator
immediately and stores all results in a fixed collection.

This gives the test several useful properties:

- every sample is processed immediately;
- `len(first_results)` is available;
- the results can be iterated more than once;
- two result snapshots can be compared by value;
- the tuple signals that the completed snapshot should not be changed.

If the outer `tuple` were removed but the generator expression remained:

```python
first_results = (detector.detect(sample) for sample in samples)
```

`first_results` would be a lazy, single-use generator. It would not support
`len`, and comparing it with another generator would compare the generator
objects rather than the generated detector results. Iterating it once would
also exhaust it.

A list comprehension would also work:

```python
first_results = [detector.detect(sample) for sample in samples]
```

The tuple is preferred here because the results represent an immutable test
snapshot. A list would be appropriate if the test needed to add, remove, or
replace results later.

The variable `detector` is already a `RegexDetector` instance:

```python
detector = RegexDetector()
```

Therefore, the loop calls `detector.detect(sample)`. It does not need to create
a new detector with `RegexDetector().detect(sample)` for every sample.

### What does `zip` do in the smoke-test loop?

The loop is:

```python
for sample, result in zip(samples, first_results):
```

`zip` pairs values from multiple iterables by position. Conceptually, it
produces:

```text
(samples[0], first_results[0])
(samples[1], first_results[1])
(samples[2], first_results[2])
...
```

Each loop iteration therefore receives the source sample and the detector
result created from that sample. This makes assertions such as the following
straightforward:

```python
assert result.sample_id == sample.sample_id
assert finding.span.end <= len(sample.text)
```

Without `zip`, the test could use an index:

```python
for index in range(len(samples)):
    sample = samples[index]
    result = first_results[index]
```

That is more verbose and introduces an index that has no meaning outside the
pairing operation.

By default, `zip` stops when the shortest iterable is exhausted. The smoke test
first checks:

```python
assert len(first_results) == len(samples)
```

so an accidentally missing result cannot be hidden by that behaviour. Python
3.10 introduced `zip(..., strict=True)` to raise an error for unequal lengths,
but this project currently targets Python 3.9, so the explicit length assertion
provides the equivalent protection.

### What is `repr` in the raw-value assertion?

`repr` is a Python built-in that returns an object's developer-oriented string
representation. It is intended to expose enough structure to help with
debugging.

For dataclasses such as `DetectorResult` and `Finding`, Python generates a
representation containing their fields. A simplified result might look like:

```text
DetectorResult(
    sample_id='sample-001',
    detector_name='regex',
    findings=(
        Finding(
            entity_type=<EntityType.EMAIL: 'email'>,
            masked_value='al***@example.com',
        ),
    ),
)
```

The smoke-test assertion:

```python
assert raw_value not in repr(result)
```

checks that the complete raw matched value does not appear in this printable
debug representation. This matters because object representations commonly
appear in assertion failures, exception messages, logs, notebooks, and terminal
output. If `Finding` accidentally gained a raw-value field, its dataclass
representation could expose that value.

This assertion is a useful privacy regression check, but it is not a complete
proof that raw data can never leak:

- it only checks the current `repr` output;
- it does not inspect every possible serializer or log path;
- raw data could exist internally without being included in `repr`;
- very short or common raw strings could cause accidental substring matches.

It should therefore be combined with structural and serialization checks. The
regex detector tests also verify that `Finding` has no `raw_value` field and
that the stored masked value differs from the raw source span. Future result
serialization and LLM logging will need their own privacy tests.
