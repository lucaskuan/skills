# TDD inside the loop

The loop's unit of work is a **slice**: one seam, one failing test, the minimal code that passes it. This file is the standard a slice has to meet. Read it before the first slice of a task, not after.

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `tdd`, with the parts an autonomous loop has to handle differently marked below.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Interactive TDD confirms seams with the user before writing tests. The loop cannot.** So the loop does the next best thing: it writes the seams it intends to test into the task plan **before** the first test, and posts them in the PR description. A reviewer can then disagree with the seam choice by reading the PR, which is the same objection arriving later instead of never.

If you cannot name the seam, you do not understand the task well enough to work it autonomously. Stop and surface it.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. A good test reads like a specification: "user can checkout with valid cart" states what capability exists, and survives refactors because it does not care about internal structure.

```typescript
// GOOD: observable behavior, public API, survives refactors
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

## The three anti-patterns

**Implementation-coupled.** Mocks internal collaborators, tests private methods, or verifies through a side channel like querying the database instead of using the interface. The tell: the test breaks when you refactor but behavior has not changed.

```typescript
// BAD: bypasses the interface to verify
await createUser({ name: "Alice" });
const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);

// GOOD: verifies through the interface
const user = await createUser({ name: "Alice" });
expect((await getUser(user.id)).name).toBe("Alice");
```

**Tautological.** The assertion recomputes the expected value the way the code does, so it passes by construction and can never disagree with the code.

```typescript
// BAD: expected value recomputed the same way
const expected = items.reduce((s, i) => s + i.price, 0);
expect(calculateTotal(items)).toBe(expected);

// GOOD: independent known literal
expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
```

This one is the loop's most likely failure. Generating both the test and the implementation in the same cycle makes it easy to derive the expectation from the code you just wrote. Expected values come from an independent source: a known-good literal, a worked example, the ticket's acceptance criteria.

**Horizontal slicing.** Writing all tests first, then all implementation. Bulk tests verify imagined behavior and go insensitive to real changes. Work in vertical slices: one test, one implementation, repeat, each test responding to what the last cycle taught you.

This is also what keeps the PR reviewable. A loop that writes twelve tests then twelve implementations produces one large diff. Twelve vertical slices produce twelve commits a reviewer can read in order.

## When to mock

Mock at **system boundaries** only: external APIs, time, randomness, sometimes the file system. Prefer a real test database over mocking the database.

Never mock your own modules, internal collaborators, or anything you control.

If the repo's conventions file says something stricter, the repo wins. Some repos ban mocked databases outright and require a real one via containers. Read the repo's conventions before the first slice.

## Rules of the loop

- **Red before green.** Write the failing test first. Run it. See it fail for the right reason, which is the assertion, not a typo or an import error. Then write only enough code to pass it.
- **A test that has never failed proves nothing.** If you wrote a test and it passed immediately, either the behavior already existed, or the test is tautological. Find out which before continuing.
- **One slice at a time.** One seam, one test, one minimal implementation, one commit.
- **No speculative code.** Do not anticipate future tests or add features no test demands.
- **Refactoring is not part of the red-green cycle.** It happens after green, as its own commit, with the tests unchanged. If a refactor requires editing tests, it is not a refactor.
