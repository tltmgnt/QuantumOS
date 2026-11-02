# Trusted-key file safety

The key-pinning workflow now creates a pin with exclusive file creation (never overwrites an existing path), requests owner-only `0600` permissions on supported systems, and rejects symbolic-link parent directories. Reading a pin rejects symlink targets, nonregular files, and hardlinked files; it uses a file descriptor with `O_NOFOLLOW` where available.

Run:

```sh
python -m unittest tests.test_gap_trusted_key_filesystem_safety -v
```

Keep the trusted-key record in a reviewer-controlled directory **outside** the untrusted audit handoff, with directory permissions that prevent unauthorized replacement. These safeguards are defense-in-depth, not a guarantee against attackers with control of parent directories or the same user account. A pin does not authenticate a human identity: independently verify the fingerprint source before creating it.
