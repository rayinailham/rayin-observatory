// Boundary and sequence tests for the illustration, not proof of the underlying DueWatch service.
import assert from 'node:assert/strict';
import { contractCategory, initialReminder, checkReminder } from '../lib/duewatch-room.ts';
for (const [days, expected] of [[61,'active'],[60,'due'],[8,'due'],[7,'renew'],[0,'renew'],[-1,'expired'],[null,'bad'],[NaN,'bad']]) {
  assert.equal(contractCategory(days).id, expected);
}
assert.deepEqual(checkReminder(initialReminder, 24), initialReminder);
let saved = checkReminder(initialReminder, 25);
assert.equal(saved.logged, true);
for (let i = 0; i < 20; i++) saved = checkReminder(saved, 25);
assert.equal(saved.logged, true);
assert.equal(saved.result, 'duplicate');
assert.equal(checkReminder({ ...initialReminder, replied: true }, 25).logged, false);
assert.equal(checkReminder({ ...saved, replied: true }, 25).result, 'replied');
assert.equal(checkReminder({ ...saved, replied: true }, 25).logged, true);
console.log('PASS: expiry boundaries, exact 24h, sequential replay, reply-before/after check');
