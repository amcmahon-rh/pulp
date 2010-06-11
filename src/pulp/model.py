#!/usr/bin/python
#
# Copyright (c) 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

from pulp.pexceptions import PulpException

class Base(dict):
    '''
    Base object that has convenience methods to get and put
    attrs into the base dict object with dot notation
    '''
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

class Repo(Base):
    def __init__(self, id, name, arch, source):
        self._id = id
        self.id = id
        self.source = source
        self.repo_source = RepoSource(source)
        self.id = id
        self.name = name
        self.arch = arch
        self.packages = dict()
        self.packagegroups = dict()
        self.packagegroupcategories = dict()
        self.comps_xml_path = "" 
        
    def get_repo_source(self):
        return RepoSource(self.source)
    
        
class RepoSource(Base):
    # yum:http://blah.bloop.com
    
    def __init__(self, url):
        self.supported_types = ['yum', 'local', 'rhn']
        self.type = None
        self.url = None
        self.parse_feed(url)
        
    def parse_feed(self, source):
        parts = source.split(':')
        if (len(parts) < 2):
            msg = "Invalid feed url.  Must be <type>:<path> where types are: %s"
            raise PulpException(msg % self.supported_types)
        if (self.supported_types.count(parts[0]) < 1):
            raise PulpException("Invalid type.  valid types are %s" 
                                % self.supported_types)
        self.type = parts[0]
        self.url = source.replace((self.type + ":"), "")

class Package(Base):
    def __init__(self, name, epoch, version, release, arch, description, 
            checksum_type, checksum, filename):
        self._id = str((name, epoch, version, release, arch, checksum))
        self.id = self._id
        self.name = name
        self.epoch = epoch
        self.version = version
        self.release = release
        self.arch = arch
        self.description = description
        self.filename = filename
        self.checksum = {checksum_type: checksum}
        # Add gpg keys
        self.requires = []
        self.provides = []

class PackageGroup(Base):
    """
    Class represents a yum.comps.Group
    """
    def __init__(self, id, name, description, user_visible=False, 
            display_order=1024, default=True, langonly=None):
        self._id = id
        self.id = id
        self.name = name
        self.description = description
        self.user_visible = user_visible
        self.display_order = display_order
        self.default = default
        self.langonly = langonly
        self.mandatory_package_names = []
        self.optional_package_names = []
        self.default_package_names = []
        self.conditional_package_names = {}
        self.translated_name = {}
        self.translated_description = {}

class PackageGroupCategory(Base):

    def __init__(self, id, name, description, display_order=99):
        self._id = id
        self.id = id
        self.name = name
        self.description = description
        self.display_order = display_order
        self.translated_name = {}
        self.translated_description = {}
        self.packagegroupids = []

class Consumer(Base):
    def __init__(self, id, description):
        self._id = id
        self.id = id
        self.description = description
        self.packageids = []
        self.repoids = []
