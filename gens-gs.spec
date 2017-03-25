%global orgname gens
Name:           %{orgname}-gs
Version:        2.16.7
Release:        7%{?dist}
Summary:        Sega Genesis, Sega CD, and Sega 32X emulator

Url:            http://segaretro.org/Gens/GS
#Most source files are GPLv2+ excludding the following, which are LGPLv2+:
#Source files for 2xsai, hq*x, super_eagle, super_2xsai, blargg_ntsc filters found in src/mdp/render/
#src/gens/ui/gtk/gtk-uri.h and src/gens/ui/gtk/gtk-uri.c
#As well, code in src/starscream uses the starscream license (non-free)
License:        GPLv2+ and LGPLv2+ and MIT and BSD and Starscream (Nonfree)
Source0:        http://segaretro.org/images/6/6d/Gens-gs-r7.tar.gz
#Found via Arch Linux: https://www.archlinux.org/packages/community/i686/gens-gs/
#Replaces deprecated gtk functions with working ones
#Cannot be sumbitted upstream, as upcomming version no longers uses GTK
Patch0:         %{name}-gtk.patch

ExclusiveArch:  i686

BuildRequires:  nasm
BuildRequires:  SDL-devel
BuildRequires:  gtk2-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  desktop-file-utils
BuildRequires:  ImageMagick
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  libpng-devel
BuildRequires:  minizip-devel
BuildRequires:  libpng-devel
Requires:       hicolor-icon-theme
Requires:       %{name}-doc

%package        doc
Summary:        Documentation Manual for Gens/GS

%description
#taken from here: http://segaretro.org/Gens/GS 
Gens/GS is a Sega Mega Drive emulator derived from Gens and maintained by
GerbilSoft. Project goals include clean source code, combined features from
various developments of Gens, and improved platform portability.

%description doc
This package contains the documentation manual for Gens/GS

%prep
%setup -q -n %{name}-r7
%patch0 -p1
#Erase all use of external libs:
sed -i '/extlib/d' configure.ac
sed -i 's/extlib//' src/Makefile.am
#Use shared minizip:
sed -i '/minizip/d' src/%{orgname}/Makefile.am
sed -i 's/"minizip\/unzip.h"/<minizip\/unzip.h>/' src/%{orgname}/util/file/decompressor/md_zip.c
#Remove all bundled code
rm -f -r src/extlib
#Rename to gens-gs to avoid conflicts:
sed -i 's/INIT(gens,/INIT(gens-gs,/' configure.ac
sed -i 's/gens.desktop/gens-gs.desktop/' xdg/Makefile.am
mv xdg/%{orgname}.desktop xdg/%{name}.desktop
#Obsolete macro in configure.ac
sed -i 's/AC_PROG_LIBTOOL/LT_INIT([disable-static])/' configure.ac

%build
autoreconf -f -i
%configure --without-7z --enable-mp3=no --with-pic \
           --disable-static --build=i686-redhat-linux \
           --docdir='%{_defaultdocdir}/%{name}-%{version}' \
           LIBS="-ldl -lX11 -lminizip"
make %{?_smp_mflags}

%install
make %{?_smp_mflags} install DESTDIR=%{buildroot}
#Use imagemagick to create a 128x128 icon from 128x96 image
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
convert images/%{orgname}_small.png -background none -gravity center -extent 128x128! %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
#Copy icons into hicolor
for size in 16 32 48; do
    dim="${size}x${size}"
    install -p -D -m 0644 images/%{orgname}gs_$dim.png \
    %{buildroot}%{_datadir}/icons/hicolor/$dim/apps/%{name}.png
done
#modify icon field in desktop to use hicolor icons
sed -i '/Icon=*/cIcon=%{name}' xdg/%{name}.desktop
#rename binary to gens-gs
mv %{buildroot}%{_bindir}/%{orgname} %{buildroot}%{_bindir}/%{name}
sed -i 's/Exec=gens/Exec=gens-gs/' xdg/%{name}.desktop
#install modified desktop file
desktop-file-install \
  --remove-key=Encoding \
  --dir %{buildroot}%{_datadir}/applications \
  xdg/%{name}.desktop
#remove any .la files that may have generated:
rm -f %{buildroot}%{_libdir}/mdp/*.la

%files
%doc README.txt NEWS.txt COPYING.txt
%{_libdir}/mdp/
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_bindir}/%{name}
%{_bindir}/mdp_test
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%files doc
%{_defaultdocdir}/%{name}-%{version}

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Sat Mar 25 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.16.7-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Nov 19 2016 Nicolas Chauvet <kwizart@gmail.com> - 2.16.7-6
- Drop BuildArch: noarch for doc - avoid pulling in x86_64 repo

* Mon Oct 27 2014 Jeremy Newton <alexjnewt@hotmail.com> - 2.16.7-5
- Patch to remove conflict with gens
- Remove prefix=/usr from configure

* Mon Oct 6 2014 Jeremy Newton <alexjnewt@hotmail.com> - 2.16.7-4
- Remove static libraries
- Created doc package
- Added Readme, News and Copying files

* Wed Jan 1 2014 Jeremy Newton <alexjnewt@hotmail.com> - 2.16.7-3
- Properly link Minizip, fix build issue

* Tue Jul 31 2012 Jeremy Newton <alexjnewt@hotmail.com> - 2.16.7-2
- Fixed License
- Disable Bundled 7zip and mpg123
- Added more build requires to avoid use of bundled code
- Manually unbundle minizip

* Tue Jul 24 2012 Jeremy Newton <alexjnewt@hotmail.com> - 2.16.7-1
- Initial working package SPEC created
