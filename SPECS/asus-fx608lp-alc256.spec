# Feature: sign module
%define sign_module 1

%global kernel_ver %(dnf repoquery kernel-devel --latest-limit=1 --queryformat="%%{VERSION}")
%global kernel_rel %(dnf repoquery kernel-devel --latest-limit=1 --queryformat="%%{RELEASE}")
%global module_dir %{_prefix}/lib/modules/%{kernel_ver}-%{kernel_rel}.%{_arch}/updates/asus-alc256
%global debug_package %{nil}

%if %{sign_module}
%define sign_tool %(gzip -c %{SOURCE3} | base64)
%endif

Name:           asus-alc256-modules
Version:        %{kernel_ver}
Release:        %{kernel_rel}
Summary:        ASUS FX608LP ALC256 headset microphone fix
License:        GPL-2.0-or-later
ExclusiveArch:  x86_64

Source0:        realtek.tar.xz
Source1:        LICENSE
Source2:        README
%if %{sign_module}
Source3:        https://github.com/fxzxmic/sign-module/releases/download/v1.0.2/sign-module
%endif

BuildRequires:  gcc make kernel-devel = %{kernel_ver}-%{kernel_rel}
BuildRequires:  kmod xz
%if %{sign_module}
BuildRequires:  gzip
%endif
Requires:       kernel-uname-r = %{kernel_ver}-%{kernel_rel}.%{_arch}
Requires:       kernel-modules-core-uname-r = %{kernel_ver}-%{kernel_rel}.%{_arch}
Requires:       module-init-tools
Provides:       asus-alc256-modules-uname-r = %{kernel_ver}-%{kernel_rel}.%{_arch}
Provides:       asus-alc256-modules-%{_arch} = %{kernel_ver}-%{kernel_rel}
Provides:       installonlypkg(kernel-module)
Supplements:    kernel-modules-uname-r = %{kernel_ver}-%{kernel_rel}.%{_arch}
%if %{sign_module}
Requires(post): %{_bindir}/base64
Requires(post): %{_bindir}/gunzip
Requires(post): libcrypto.so.3()(64bit)
Requires(post): liblzma.so.5()(64bit)
Requires(post): libc.so.6()(64bit)
Requires(post): libz.so.1()(64bit)
%endif

%description
Realtek ALC256 headset microphone cold-boot fix for ASUS FX608LP systems
with subsystem ID 1043:1064. Built from maintained Fedora kernel sources
against the matching kernel-devel package. The original Fedora modules
are preserved, and packages for different kernels can coexist.

The module is unsigned in CI. Installation signs it when a local MOK key
and certificate are available at /etc/keys/modsign.key and modsign.der.

%prep
%setup -q -n realtek

%build
test -s /usr/src/kernels/%{kernel_ver}-%{kernel_rel}.%{_arch}/Module.symvers
test "$(make -s -C /usr/src/kernels/%{kernel_ver}-%{kernel_rel}.%{_arch} kernelrelease)" = "%{kernel_ver}-%{kernel_rel}.%{_arch}"
%{make_build} -C /usr/src/kernels/%{kernel_ver}-%{kernel_rel}.%{_arch} M="$PWD" modules

strip --strip-unneeded *.ko
xz --check=crc32 -9 *.ko

%install
install -d %{buildroot}%{module_dir}
install -m 0644 *.ko.xz %{buildroot}%{module_dir}/
install -d %{buildroot}%{_prefix}/lib/depmod.d
cat > %{buildroot}%{_prefix}/lib/depmod.d/asus-alc256-%{kernel_ver}-%{kernel_rel}.conf <<EOF
override snd-hda-codec-alc269 %{kernel_ver}-%{kernel_rel}.%{_arch} updates/asus-alc256
EOF
install -Dm0644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}-%{version}-%{release}/LICENSE
install -Dm0644 %{SOURCE2} %{buildroot}%{_docdir}/%{name}-%{version}-%{release}/README

%check
for module in snd-hda-codec-alc269; do
    test "$(modinfo -F vermagic "$module.ko.xz" | cut -d ' ' -f1)" = "%{kernel_ver}-%{kernel_rel}.%{_arch}"
    test -z "$(modinfo -F signer "$module.ko.xz")"
    modinfo "$module.ko.xz"
done

%post
%if %{sign_module}
if [ -f %{_sysconfdir}/keys/modsign.key ] && [ -f %{_sysconfdir}/keys/modsign.der ]; then
    chown root:root %{_sysconfdir}/keys/modsign.*
    chmod 400 %{_sysconfdir}/keys/modsign.key
    chmod 444 %{_sysconfdir}/keys/modsign.der
    base64 -d << EOF | gunzip > %{_tmppath}/sign-module
%{sign_tool}
EOF
    chmod +x %{_tmppath}/sign-module
    for module in /lib/modules/%{kernel_ver}-%{kernel_rel}.%{_arch}/updates/asus-alc256/snd-hda-codec-*.ko*; do
        %{_tmppath}/sign-module sha256 %{_sysconfdir}/keys/modsign.key %{_sysconfdir}/keys/modsign.der $module
    done
    rm -f %{_tmppath}/sign-module
fi
%endif
/sbin/depmod -a %{kernel_ver}-%{kernel_rel}.%{_arch}

%postun
/sbin/depmod -a %{kernel_ver}-%{kernel_rel}.%{_arch}

%files
%defattr(-,root,root,-)
%license %{_licensedir}/%{name}-%{version}-%{release}/
%doc %{_docdir}/%{name}-%{version}-%{release}/
%{module_dir}/
%{_prefix}/lib/depmod.d/asus-alc256-%{kernel_ver}-%{kernel_rel}.conf

%changelog
