# Copyright (c) 2000-2008, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support 0
# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define section free

Summary:        Analyse and modify class dependencies
Name:           vafer-dependency
Version:        0.4
Release:        %mkrel 2.0.2
Epoch:          0
License:        Apache Software License 2.0
URL:            https://vafer.org/projects/dependency/
Group:          Development/Java
Source0:        vafer-dependency-0.4.tar.gz
# svn export http://vafer.org/svn/projects/dependency/ vafer-dependency-0.4/

Source3:        vafer-dependency-0.4-jpp-depmap.xml
Source4:        vafer-dependency-autogenerated-files.tar.gz
Patch0:         vafer-dependency-0.4-pom.patch

BuildRequires:  jpackage-utils >= 0:1.7.4
BuildRequires:  java-rpmbuild
BuildRequires:  ant >= 0:1.6.5
BuildRequires:  ant-junit
BuildRequires:  junit >= 0:3.8.1
%if %{with_maven}
BuildRequires:  maven2 >= 2.0.4-9
BuildRequires:  maven2-plugin-ant
BuildRequires:  maven2-plugin-antrun
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-dependency
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven-surefire-plugin
BuildRequires:  maven2-common-poms >= 1.0
%endif
BuildRequires:  asm2
BuildRequires:  jakarta-commons-io
Requires:  asm2
Requires:  jakarta-commons-io
Requires:  java >= 0:1.5.0

Requires(post):    jpackage-utils >= 0:1.7.4
Requires(postun):  jpackage-utils >= 0:1.7.4

%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

%description
This library provides an API to analyse and modify class 
dependencies. It provides the core to the maven2 minijar 
plugin and provides something in the middle between 
jarjar and proguard.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%prep
%setup -q 
# don't: these are test input files
#for j in $(find . -name "*.jar"); do
#    mv $j $j.no
#done
gzip -dc %{SOURCE4} | tar xf -


%patch0 -b .sav0

%build
export JAVA_HOME=%{_jvmdir}/java-rpmbuild
export CLASSPATH=$JAVA_HOME/lib/tools.jar
%if %{with_maven}
mkdir external_repo
ln -s %{_javadir} external_repo/JPP

export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp \
        -e \
        -Dmaven2.jpp.depmap.file=%{SOURCE3} \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        ant:ant install javadoc:javadoc

%else
export CLASSPATH=$(build-classpath \
asm2/asm2-analysis \
asm2/asm2-commons \
asm2/asm2-tree \
asm2/asm2-util \
asm2/asm2 \
commons-io \
)
CLASSPATH=$CLASSPATH:target/classes:target/test-classes
%ant -Dmaven.settings.offline=true -Dbuild.sysclasspath=only jar test javadoc
%endif

%install
rm -rf $RPM_BUILD_ROOT

# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p target/dependency-%{version}.jar \
      $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

%add_to_maven_depmap org.vafer dependency %{version} JPP %{name}


# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 pom.xml \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 

# manual
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp LICENSE.txt $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%{gcj_compile}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}/LICENSE.txt
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%{gcj_files}

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}
