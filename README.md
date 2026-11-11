# ASUS ALC256 headset microphone fix

A Linux headset microphone fix for ASUS FX608LP laptops with a Realtek ALC256
codec (`10ec:0256`) and subsystem ID `1043:1064`.

On affected systems, a TRRS headset connected before power-on produces noise or
silence when recording. Unplugging and reconnecting the headset restores the
microphone. This driver adds an initialization sequence derived from the OEM
audio driver, before Linux configures the headset pins.

Cold-boot headset microphone recording has been verified on an ASUS TX Gaming
FX608LP with Fedora kernel 7.2.11 and BIOS FX608LP.315. The Fedora 45 build
uses 7.3.x sources and has not yet been tested on hardware.

## Installation

Download the RPM matching the installed kernel and architecture from
[Releases](https://github.com/fxzxmicah/ASUS-ALC256-10431064/releases).
The RPM version and release correspond to the Fedora kernel version and release.
Install it using the system package manager, for example:

```sh
run0 --via-shell dnf install ./asus-alc256-modules-*.rpm
```

Select a single matching RPM when several downloads are present. To replace an
already installed build with the same version and release, use `dnf reinstall`
instead of `dnf install`.

The package installs `snd_hda_codec_alc269` under `updates/asus-alc256` and gives
that directory precedence for the target kernel. It keeps Fedora's original
modules intact and supports packages for multiple kernel versions.

### Secure Boot

Release modules are unsigned. During installation, the RPM signs them using
`/etc/keys/modsign.key` and `/etc/keys/modsign.der` if both files exist. The private
key stays on the local computer. If either file is absent, signing is skipped.
With Secure Boot enforcement, the modules need a signature from a trusted key.

An existing module-signing key can be used. Check enrollment with:

```sh
mokutil --test-key /etc/keys/modsign.der
```

If the certificate is not enrolled, import it with `mokutil --import` and complete
enrollment in the firmware MOK manager. Do not disable Secure Boot.

### Module selection

The package runs `depmod` after installation and removal.

After rebooting into the target kernel, check the selected path and signature:

```sh
modinfo -n snd_hda_codec_alc269
modinfo -F signer snd_hda_codec_alc269
```

The path should contain `updates/asus-alc256`. `modinfo` describes the module on
disk; compare its `srcversion` with
`/sys/module/snd_hda_codec_alc269/srcversion` to check the loaded build as well.

## Removal

Remove the package for the affected kernel using the package manager. Fedora's
original modules become the selected modules again after rebooting. Packages
for other kernel versions can remain installed.

## Building

The branch name selects the Fedora container version. Run the GitHub Actions
workflow to build RPMs for that branch's latest available Fedora kernel. Enable
`rebuild` to replace its latest release. No local compiler is needed.

The driver is based on Fedora kernel sources. See [source provenance](FEDORA)
and the [driver patch](0001-asus-fx608lp-coldboot.patch) for details.

## Compatibility

The quirk is selected automatically for subsystem ID `1043:1064`. For explicit
testing on another ALC256 system, `snd_hda_intel.model=alc256-asus-fx608lp` selects
the same quirk. This does not imply compatibility with that system. When several
HDA controllers are present, the model option must address the intended
controller. Automatic selection on FX608LP requires no model option.

## License

[GPL-2.0-or-later](SOURCES/LICENSE), matching the imported Realtek driver sources.
