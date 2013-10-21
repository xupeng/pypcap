#!/usr/bin/env python
#
# $Id$

from distutils.core import setup, Extension
import glob, os, sys
import subprocess

pcap_config = {}

def _write_config_h(cfg):
    # XXX - write out config.h for pcap_ex.c
    d = {}
    if os.path.exists(os.path.join(cfg['include_dirs'][0], 'pcap-int.h')):
        d['HAVE_PCAP_INT_H'] = 1
    buf = open(os.path.join(cfg['include_dirs'][0], 'pcap.h')).read()
    if buf.find('pcap_file(') != -1:
        d['HAVE_PCAP_FILE'] = 1
    if buf.find('pcap_compile_nopcap(') != -1:
        d['HAVE_PCAP_COMPILE_NOPCAP'] = 1
    if buf.find('pcap_setnonblock(') != -1:
        d['HAVE_PCAP_SETNONBLOCK'] = 1
    f = open('config.h', 'w')
    for k, v in d.iteritems():
        f.write('#define %s %s\n' % (k, v))

def _pcap_config(dirs=[ None ]):
    cfg = {}
    if not dirs[0]:
        dirs = [ '/usr', sys.prefix ] + glob.glob('/opt/libpcap*') + \
               glob.glob('../libpcap*') + glob.glob('../wpdpack*')
    for d in dirs:
        for sd in ('include/pcap', 'include', ''):
            incdirs = [ os.path.join(d, sd) ]
            if os.path.exists(os.path.join(d, sd, 'pcap.h')):
                cfg['include_dirs'] = [ os.path.join(d, sd) ]
                for sd in ('lib', 'lib64', ''):
                    for lib in (('pcap', 'libpcap.a'),
                                ('pcap', 'libpcap.so'),
                                ('pcap', 'libpcap.dylib'),
                                ('wpcap', 'wpcap.lib')):
                        if os.path.exists(os.path.join(d, sd, lib[1])):
                            cfg['library_dirs'] = [ os.path.join(d, sd) ]
                            cfg['libraries'] = [ lib[0] ]
                            if lib[0] == 'wpcap':
                                cfg['libraries'].append('iphlpapi')
                                cfg['extra_compile_args'] = \
                                    [ '-DWIN32', '-DWPCAP' ]
                            print 'found', cfg
                            _write_config_h(cfg)
                            return cfg
    raise Exception("couldn't find pcap build or installation directory")

try:
    subprocess.check_call(['which', 'pyrexc'])
except subprocess.CalledProcessError:
    pass
else:
    subprocess.check_call(['pyrexc', 'pcap.pyx'])
pcap_config = _pcap_config()

pcap = Extension(name='pcap',
                 sources=[ 'pcap.c', 'pcap_ex.c' ],
                 include_dirs=pcap_config.get('include_dirs', ''),
                 library_dirs=pcap_config.get('library_dirs', ''),
                 libraries=pcap_config.get('libraries', ''),
                 extra_compile_args=pcap_config.get('extra_compile_args', ''))

setup(name='pcap',
      version='1.1',
      author='Dug Song',
      author_email='dugsong@monkey.org',
      url='http://monkey.org/~dugsong/pypcap/',
      description='packet capture library',
      ext_modules = [ pcap ],
      install_requires=['Pyrex'])
