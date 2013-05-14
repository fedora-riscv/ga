Name:    ga
Version: 5.1.1
Release: 2%{?dist}
Summary: Global Arrays Toolkit
License: BSD
Source: http://www.emsl.pnl.gov/docs/global/download/%{name}-5-1-1.tgz
URL: http://www.emsl.pnl.gov/docs/global
%if 0%{?rhel} <= 6
ExclusiveArch: i386 x86_64
%else
ExclusiveArch: i586 x86_64
%endif
BuildRequires: openmpi-devel, mpich2-devel, gcc-c++, gcc-gfortran, hwloc-devel
BuildRequires: libibverbs-devel, atlas-devel, openssh-clients, dos2unix
BuildRoot: %{_tmppath}/%{name}-%{version}

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

%define ga_mpi_common() \
%package %{1} \
Summary: Global Arrays Toolkit for %{1} \
BuildRequires: scalapack-%{1}-devel, blacs-%{1}-devel \
Requires: %{name}-common = %{version} \
%description %{1} \
%{ga_desc_base} \
- Libraries against %{1}. \
%package %{1}-devel \
Summary: Global Arrays Toolkit for %{1} Development \
Requires: scalapack-%{1}-devel, blacs-%{1}-devel, %{1}-devel \
Requires: atlas-devel, %{name}-common = %{version}, %{name}-%{1} = %{version} \
%description %{1}-devel \
%{ga_desc_base} \
- Development Software against %{1}. \
%package %{1}-static \
Summary: Global Arrays Toolkit for %{1} Static Libraries \
Requires: scalapack-%{1}-devel, blacs-%{1}-devel, %{1}-devel \
Requires: atlas-devel, %{name}-common = %{version}, %{name}-%{1} = %{version} \
%description %{1}-static \
%{ga_desc_base} \
- Static Libraries against %{1}. \
%post %{1} -p /sbin/ldconfig \
%postun %{1} -p /sbin/ldconfig

%ga_mpi_common mpich2
%ga_mpi_common openmpi

%define ga_version 5-1-1

%prep
%setup -q -c -n %{name}-%{version}
for i in mpich2 openmpi; do
  cp -a %{name}-%{ga_version} %{name}-%{version}-$i
done

%build
%define doBuild() \
export LIBS="-lscalapack -lmpiblacs -lmpiblacsCinit -lmpiblacsF77init -L%{_libdir}/atlas -lf77blas -llapack -lm" ; \
cd %{name}-%{version}-$MPI_COMPILER_NAME ; \
%configure \\\
  --bindir=$MPI_BIN \\\
  --libdir=$MPI_LIB \\\
  --includedir=$MPI_INCLUDE \\\
  --with-altas=%{_libdir}/atlas \\\
  --with-scalapack=$MPI_LIB \\\
  --enable-shared \\\
  --enable-static \\\
  --enable-cxx \\\
  --enable-f77 \\\
  %{?1} ; \
%{__make} %{?__smp_mflags} ; \
cd ..

export MPI_COMPILER_NAME=mpich2
%{_mpich2_load}
%doBuild
%{_mpich2_unload}

export MPI_COMPILER_NAME=openmpi
%{_openmpi_load}
%doBuild --with-openib
%{_openmpi_unload}

%install
%define doInstall \
cd %{name}-%{version}-$MPI_COMPILER_NAME ; \
DESTDIR=$RPM_BUILD_ROOT make install ; \
cd ..

rm -rf $RPM_BUILD_ROOT
export MPI_COMPILER_NAME=mpich2
%{_mpich2_load}
%doInstall
%{_mpich2_unload}

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
%{_mpich2_load}
cd %{name}-%{version}-mpich2
make check
cd ..
%{_mpich2_unload}
%endif

%clean
rm -rf %{buildroot}

%files common
%doc %{name}-%{ga_version}/README %{name}-%{ga_version}/NEWS
%doc %{name}-%{ga_version}/COPYRIGHT
%config(noreplace) %{_sysconfdir}/sysctl.d/armci.conf

%define ga_files() \
%files %{1} \
%doc %{name}-%{ga_version}/COPYRIGHT \
%{_libdir}/%{1}/lib/lib*.so.* \
%{_libdir}/%{1}/bin/*.x \
%files %{1}-devel \
%doc %{name}-%{ga_version}/COPYRIGHT \
%{_libdir}/%{1}/lib/lib*.so \
%{_includedir}/%{1}-%{_arch}/* \
%{_libdir}/%{1}/bin/ga-config \
%files %{1}-static \
%doc %{name}-%{ga_version}/COPYRIGHT \
%{_libdir}/%{1}/lib/lib*.a \

%ga_files mpich2
%ga_files openmpi

%changelog
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

