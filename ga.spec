%define mpich_name mpich

Name:    ga
Version: 5.3b
Release: 22%{?dist}
Summary: Global Arrays Toolkit
License: BSD
Source: http://hpc.pnl.gov/globalarrays/download/%{name}-5-3b.tgz
Patch0: ga-5-format-security.patch
URL: http://hpc.pnl.gov/globalarrays/
ExclusiveArch: %{ix86} x86_64
BuildRequires: openmpi-devel, %{mpich_name}-devel, gcc-c++, gcc-gfortran, hwloc-devel
BuildRequires: libibverbs-devel, atlas-devel, openssh-clients, dos2unix
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%define ga_desc_base \
The Global Arrays (GA) toolkit provides an efficient and portable \
"shared-memory" programming interface for distributed-memory \
computers. Each process in a MIMD parallel program can asynchronously \
access logical blocks of physically distributed dense multi- \
dimensional arrays, without need for explicit cooperation by other \
processes. Unlike other shared-memory environments, the GA model \
exposes to the programmer the non-uniform memory access (NUMA) \
characteristics of the high performance computers and acknowledges \
that access to a remote portion of the shared data is slower than to \
the local portion. The locality information for the shared data is \
available, and a direct access to the local portions of shared data \
is provided.

%description
%{ga_desc_base}
- Global Arrays Toolkit Base Package.

%package common
Summary: Global Arrays Common Files
BuildArch: noarch
%description common
%{ga_desc_base}
- Global Arrays Common Files.

%package mpich
Summary: Global Arrays Toolkit for MPICH
BuildRequires: scalapack-%{mpich_name}-devel, blacs-%{mpich_name}-devel
BuildRequires: lapack-devel
Requires: %{name}-common = %{version}
Provides: %{name}-mpich2 = %{version}-%{release}
Obsoletes: %{name}-mpich2 < %{version}-%{release}
%description mpich
%{ga_desc_base}
- Libraries against MPICH.
%package mpich-devel
Summary: Global Arrays Toolkit for MPICH Development
Requires: scalapack-%{mpich_name}-devel, blacs-%{mpich_name}-devel, %{mpich_name}-devel
Requires: lapack-devel
Requires: atlas-devel, %{name}-common = %{version}, %{name}-mpich = %{version}
Provides: %{name}-mpich2-devel = %{version}-%{release}
Obsoletes: %{name}-mpich2-devel < %{version}-%{release}
%description mpich-devel
%{ga_desc_base}
- Development Software against MPICH.
%package mpich-static
Summary: Global Arrays Toolkit for MPICH Static Libraries
Requires: scalapack-%{mpich_name}-devel, blacs-%{mpich_name}-devel, %{mpich_name}-devel
Requires: lapack-devel
Requires: atlas-devel, %{name}-common = %{version}, %{name}-mpich = %{version}
Provides: %{name}-mpich2-static = %{version}-%{release}
Obsoletes: %{name}-mpich2-static < %{version}-%{release}
%description mpich-static
%{ga_desc_base}
- Static Libraries against MPICH.
%post mpich -p /sbin/ldconfig
%postun mpich -p /sbin/ldconfig

%package openmpi
Summary: Global Arrays Toolkit for OpenMPI
BuildRequires: scalapack-openmpi-devel, blacs-openmpi-devel
BuildRequires: lapack-devel
Requires: %{name}-common = %{version}
%description openmpi
%{ga_desc_base}
- Libraries against OpenMPI.
%package openmpi-devel
Summary: Global Arrays Toolkit for OpenMPI Development
Requires: scalapack-openmpi-devel, blacs-openmpi-devel, openmpi-devel
Requires: lapack-devel
Requires: atlas-devel, %{name}-common = %{version}, %{name}-openmpi = %{version}
%description openmpi-devel
%{ga_desc_base}
- Development Software against OpenMPI.
%package openmpi-static
Summary: Global Arrays Toolkit for OpenMPI Static Libraries
Requires: scalapack-openmpi-devel, blacs-openmpi-devel, openmpi-devel
Requires: atlas-devel, %{name}-common = %{version}, %{name}-openmpi = %{version}
%description openmpi-static
%{ga_desc_base}
- Static Libraries against OpenMPI.
%post openmpi -p /sbin/ldconfig
%postun openmpi -p /sbin/ldconfig

%define ga_version 5-3b

%prep
%setup -q -c -n %{name}-%{version}
pushd %{name}-%{ga_version}
%patch0 -p1
popd
for i in mpich openmpi; do
  cp -a %{name}-%{ga_version} %{name}-%{version}-$i
done

%build
%if 0%{?rhel} >= 7
%define atlas_libs -lsatlas
%endif
%if 0%{?fedora}%{?rhel} == 19
%define atlas_libs -lsatlas
%endif
%if 0%{?fedora}%{?rhel} == 20
%define atlas_libs -latlas -lcblas -lclapack -lf77blas -llapack -lptcblas -lptf77blas
%endif
%if 0%{?fedora}%{?rhel} >= 21
%define atlas_libs -lsatlas
%endif
%if 0%{?rhel} == 6
%define atlas_libs -lf77blas -llapack
%endif

%if 0%{?fedora} >= 21
%global blacs_libs -lmpiblacs
%else
%global	blacs_libs -lmpiblacs
%endif

%define doBuild \
export LIBS="-lscalapack %{blacs_libs} -L%{_libdir}/atlas %{atlas_libs} -lm" ; \
cd %{name}-%{version}-$MPI_COMPILER_NAME ; \
%configure \\\
  --bindir=$MPI_BIN \\\
  --libdir=$MPI_LIB \\\
  --includedir=$MPI_INCLUDE \\\
  --with-altas=%{_libdir}/atlas \\\
  --with-scalapack=$MPI_LIB \\\
  --enable-shared \\\
  --enable-static \\\
  --enable-peigs \\\
  --enable-cxx \\\
  --enable-f77 \\\
  $GA_CONFIGURE_OPTIONS ; \
%{__make} %{?__smp_mflags} ; \
cd ..

export MPI_COMPILER_NAME=mpich
export GA_CONFIGURE_OPTIONS=""
%{_mpich_load}
%doBuild
%{_mpich_unload}

export MPI_COMPILER_NAME=openmpi
export GA_CONFIGURE_OPTIONS="--with-openib"
%{_openmpi_load}
%doBuild
%{_openmpi_unload}

%install
%define doInstall \
cd %{name}-%{version}-$MPI_COMPILER_NAME ; \
DESTDIR=$RPM_BUILD_ROOT make install ; \
cd ..

rm -rf $RPM_BUILD_ROOT
export MPI_COMPILER_NAME=mpich
%{_mpich_load}
%doInstall
%{_mpich_unload}

export MPI_COMPILER_NAME=openmpi
%{_openmpi_load}
%doInstall
%{_openmpi_unload}

find %{buildroot} -type f -name "*.la" -exec rm -f {} \;

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysctl.d
echo 'kernel.shmmax = 134217728' > $RPM_BUILD_ROOT/%{_sysconfdir}/sysctl.d/armci.conf
dos2unix %{name}-%{ga_version}/COPYRIGHT

%check
%if %{?do_test}0
%{_mpich_load}
cd %{name}-%{version}-mpich
make check
cd ..
%{_mpich_unload}
%endif

%clean
rm -rf %{buildroot}

%files common
%doc %{name}-%{ga_version}/README %{name}-%{ga_version}/NEWS
%doc %{name}-%{ga_version}/COPYRIGHT
%config(noreplace) %{_sysconfdir}/sysctl.d/armci.conf

%files mpich
%doc %{name}-%{ga_version}/COPYRIGHT
%{_libdir}/%{mpich_name}/lib/lib*.so.*
%{_libdir}/%{mpich_name}/bin/*.x
%files mpich-devel
%doc %{name}-%{ga_version}/COPYRIGHT
%{_libdir}/%{mpich_name}/lib/lib*.so
%{_includedir}/%{mpich_name}-%{_arch}/*
%{_libdir}/%{mpich_name}/bin/ga-config
%files mpich-static
%doc %{name}-%{ga_version}/COPYRIGHT
%{_libdir}/%{mpich_name}/lib/lib*.a

%files openmpi
%doc %{name}-%{ga_version}/COPYRIGHT
%{_libdir}/openmpi/lib/lib*.so.*
%{_libdir}/openmpi/bin/*.x
%files openmpi-devel
%doc %{name}-%{ga_version}/COPYRIGHT
%{_libdir}/openmpi/lib/lib*.so
%{_includedir}/openmpi-%{_arch}/*
%{_libdir}/openmpi/bin/ga-config
%files openmpi-static
%doc %{name}-%{ga_version}/COPYRIGHT
%{_libdir}/openmpi/lib/lib*.a

%changelog
* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.3b-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Oct 21 2016 Orion Poplawski <orion@cora.nwra.com> - 5.3b-21
- Rebuild for openmpi 2.0

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.3b-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Sep 15 2015 Orion Poplawski <orion@cora.nwra.com> - 5.3b-19
- Rebuild for openmpi 1.10.0

* Sun Jul 26 2015 Sandro Mani <manisandro@gmail.com> - 5.3b-18
- Rebuild for RPM MPI Requires Provides Change

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3b-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 5.3b-16
- Rebuilt for GCC 5 C++11 ABI change

* Fri Mar 20 2015 David Brown <david.brown@pnnl.gov> - 5.3b-15
- Rebuild to support new version of mpich

* Wed Nov 19 2014 David Brown <david.brown@pnnl.gov> - 5.3b-14
- Fix bug #1150473 to support epel7

* Wed Oct 29 2014 David Brown <david.brown@pnnl.gov> - 5.3b-13
- Rebuild to fix bug #1155077

* Sun Oct 5 2014 David Brown <david.brown@pnnl.gov> - 5.3b-12
- Fix up some conditions for f22
- Add more dependancies on lapack-devel in right places

* Tue Sep 30 2014 David Brown <david.brown@pnnl.gov> - 5.3b-11
- Rebuilt for updated upstream package

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3b-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jul 07 2014 David Brown <david.brown@pnnl.gov> - 5.3b-8
- add explicit requires for mpich and openmpi packages (#1116627)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3b-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon May 12 2014 Tom Callaway <spot@fedoraproject.org> - 5.3b-7
- rebuild against new blacs

* Thu Mar 27 2014 David Brown <david.brown@pnnl.gov> - 5.3b-6
- version bump to get all fedora/epel versions in sync

* Thu Mar 27 2014 David Brown <david.brown@pnnl.gov> - 5.3b-5
- Parameterize mpich name and environment loading to cover EPEL

* Thu Mar 27 2014 David Brown <david.brown@pnnl.gov> - 5.3b-4
- Update to include configure option fixes (1081403)

* Sun Feb 23 2014 David Brown <david.brown@pnnl.gov> - 5.3b-3
- Updated revision for new mpich

* Wed Feb 5 2014 David Brown <david.brown@pnnl.gov> - 5.3b-2
- Fix BuildRoot
- add more generic/specific atlas config

* Mon Jan 27 2014 David Brown <david.brown@pnnl.gov> - 5.3b-1
- Update to upstream version
- Fix exclusive arch to match documentation
- add patch for format security fixes (1037075)

* Mon Sep 23 2013 David Brown <david.brown@pnnl.gov> - 5.1.1-8
- Rebuild for updated atlas.
- Fix atlas libs since they changed things

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 22 2013 David Brown <david.brown@pnnl.gov> - 5.1.1-6
- forgot obsoletes and provides for sub packages as well.

* Mon Jul 22 2013 David Brown <david.brown@pnnl.gov> - 5.1.1-5
- forgot about obsoletes and provides for new mpich packages.

* Mon Jul 15 2013 David Brown <david.brown@pnnl.gov> - 5.1.1-4
- Rebuild for updated openmpi
- resolved issues with doBuild function to proper define
- also renamed mpich2 to mpich

* Tue May 21 2013 David Brown <david.brown@pnnl.gov> - 5.1.1-3
- modify exclusive arch some more (964424, 964946)

* Tue May 14 2013 David Brown <david.brown@pnnl.gov> - 5.1.1-2
- Add exclusive arch for EPEL.
- And lib*.la files are bad too.

* Wed May 1 2013 David Brown <david.brown@pnnl.gov> - 5.1.1-1
- Update to upstream version
- fixed file locations and clean up rpmlint

* Thu Jul 5 2012 David Brown <david.brown@pnnl.gov> - 5.1-2
- added common package with license and sysctl additions

* Mon Apr 9 2012 David Brown <david.brown@pnnl.gov> - 5.1-1
- initial packaging

