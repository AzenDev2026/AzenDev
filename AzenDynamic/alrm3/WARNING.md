## Deep sleep defect — reported 2026-09-25

### Symptom

On some machines (confirmed: Dell XPS 13, possibly others), the `deep`
(ACPI S3) sleep mode causes the screen to go black when the lid is closed
or sleep is entered, and the system cannot be woken up.

### Root cause

Those machines do not really support traditional S3. Forcing `deep` puts
the machine into a state it cannot resume from. Only `s2idle` is reliable
there.

### Workaround for affected users

Disable the whole service and set the sleep mode back to `s2idle` in your
bootloader kernel parameters.

    sudo systemctl disable --now azen-alrm.service
    sudo systemctl mask azen-alrm.service

Then add `mem_sleep_default=s2idle` to your kernel command line and reboot.

### Status: fixed — 2026-09-27

`sleep_manager.cpp` no longer selects `deep` in any power or mode
combination. Every path in `apply_config()` now goes through the new
`enable_safe_sleep()` helper, which prefers `s2idle` and only falls back to
`deep` when the hardware does not advertise `s2idle` at all — and logs a
warning when it does so.

The earlier fix (2026-09-25) only covered the energy-saver and performance
branches; balanced mode on battery still forced `deep`, which is why the
defect could still be hit on a normal laptop with the lid closed.

> Note: this fix lives in the source tree. If you installed an older build
> from a release archive, reinstall to pick it up.
