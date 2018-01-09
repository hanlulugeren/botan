#!/usr/bin/python2

"""
(C) 2016 Jack Lloyd
(C) 2017 Fabian Weissberg, Rohde & Schwarz Cybersecurity

Botan is released under the Simplified BSD License (see license.txt)
"""

import sys
import datetime
import re
from collections import defaultdict


def format_map(m, for_oid = False):
    s = ''
    for k in sorted(m.keys()):
        v = m[k]

        if len(s) > 0:
            s += '      '

        if for_oid:
            s += '{ "%s", OID("%s") },\n' % (k,v)
        else:
            s += '{ "%s", "%s" },\n' % (k,v)

    s = s[:-2] # chomp last two chars

    return s


def format_as_map(oid2str, str2oid):
   return """/*
* OID maps
*
* This file was automatically generated by %s on %s
*
* All manual edits to this file will be lost. Edit the script
* then regenerate this source file.
*
* Botan is released under the Simplified BSD License (see license.txt)
*/

#include <botan/oids.h>
#include <unordered_map>

namespace Botan {

std::unordered_map<std::string, std::string> OIDS::load_oid2str_map()
   {
   return std::unordered_map<std::string,std::string>{
      %s
      };
   }

std::unordered_map<std::string, OID> OIDS::load_str2oid_map()
   {
   return std::unordered_map<std::string,OID>{
      %s
      };
   }

}
""" % (sys.argv[0], datetime.date.today().strftime("%Y-%m-%d"),
       format_map(oid2str), format_map(str2oid, True))


def format_if(m, nm,t=False):
    s = ''
    for k in sorted(m.keys()):
        v = m[k]

        if t:
            s += '   if(%s == "%s") return OID("%s");\n' % (nm,k, v)
        else:
            s += '   if(%s == "%s") return "%s";\n' % (nm,k, v)

    s = s[:-1]

    return s

def format_as_ifs(oid2str, str2oid):
   return """/*
* OID maps
*
* This file was automatically generated by %s on %s
*
* All manual edits to this file will be lost. Edit the script
* then regenerate this source file.
*
* Botan is released under the Simplified BSD License (see license.txt)
*/

#include <botan/oids.h>

namespace Botan {

namespace OIDS {

std::string lookup(const OID& oid)
   {
   const std::string oid_str = oid.as_string();
%s

#if defined(BOTAN_HOUSE_ECC_CURVE_NAME)
   if(oid_str == BOTAN_HOUSE_ECC_CURVE_OID) return BOTAN_HOUSE_ECC_CURVE_NAME;
#endif

   return std::string();
   }

OID lookup(const std::string& name)
   {
%s

#if defined(BOTAN_HOUSE_ECC_CURVE_NAME)
   if(name == BOTAN_HOUSE_ECC_CURVE_NAME) return OID(BOTAN_HOUSE_ECC_CURVE_OID);
#endif

   return OID();
   }

}

}
""" % (sys.argv[0], datetime.date.today().strftime("%Y-%m-%d"),
       format_if(oid2str,"oid_str"), format_if(str2oid, "name", True))


def format_dn_ub_map(dn_ub, oid2str):
    s = ''
    for k in sorted(dn_ub.keys()):
        v = dn_ub[k]

        s += '   { Botan::OID("%s"), %s }, // %s\n' % (k,v,oid2str[k])

    # delete last ',' and \n
    idx = s.rfind(',')
    if idx != -1:
        s = s[:idx] + s[idx+1:-1]

    return s


def format_dn_ub_as_map(dn_ub, oid2str):
    return """/*
* DN_UB maps: Upper bounds on the length of DN strings
*
* This file was automatically generated by %s on %s
*
* All manual edits to this file will be lost. Edit the script
* then regenerate this source file.
*
* Botan is released under the Simplified BSD License (see license.txt)
*/

#include <botan/x509_dn.h>
#include <botan/asn1_oid.h>
#include <map>

namespace {
/**
 * Upper bounds for the length of distinguished name fields as given in RFC 5280, Appendix A.
 * Only OIDS recognized by botan are considered, so far.
 * Maps OID string representations instead of human readable strings in order
 * to avoid an additional lookup.
 */
static const std::map<Botan::OID, size_t> DN_UB =
   {
%s
   };
}

namespace Botan {

//static
size_t X509_DN::lookup_ub(const OID& oid)
   {
   auto ub_entry = DN_UB.find(oid);
   if(ub_entry != DN_UB.end())
      {
      return ub_entry->second;
      }
   else
      {
      return 0;
      }
   }
}
""" % (sys.argv[0], datetime.date.today().strftime("%Y-%m-%d"),
       format_dn_ub_map(dn_ub,oid2str))


def format_set_map(m):
    s = ''
    for k in sorted(m.keys()):
        v = m[k]

        if len(s) > 0:
            s += '   '

        s += '{ "%s", {' % k
        for pad in v:
            s += '"%s", ' % pad
        if len(v) is not 0:
            s = s[:-2]
        s += '} },\n'
    s = s[:-1]
    return s


def format_pads_as_map(sig_dict):
    return """/*
* Sets of allowed padding schemes for public key types
*
* This file was automatically generated by %s on %s
*
* All manual edits to this file will be lost. Edit the script
* then regenerate this source file.
*
* Botan is released under the Simplified BSD License (see license.txt)
*/

#include <botan/internal/padding.h>
#include <map>
#include <vector>
#include <string>
#include <algorithm>

namespace Botan {

const std::map<const std::string, std::vector<std::string>> allowed_signature_paddings =
   {
   %s
   };

__attribute__((visibility("default"))) const std::vector<std::string> get_sig_paddings(const std::string algo)
   {
   if(allowed_signature_paddings.count(algo) > 0)
      return allowed_signature_paddings.at(algo);
   return {};
   }

bool sig_algo_and_pad_ok(const std::string algo, std::string padding)
   {
   std::vector<std::string> pads = get_sig_paddings(algo);
   return std::find(pads.begin(), pads.end(), padding) != pads.end();
   }
}
""" % (sys.argv[0], datetime.date.today().strftime("%Y-%m-%d"),
       format_set_map(sig_dict))


def main(args = None):
    """ Print header files (oids.cpp, dn_ub.cpp) depending on the first argument and on srs/build-data/oids.txt

        Choose 'oids' to print oids.cpp, needs to be written to src/lib/asn1/oids.cpp
        Choose 'dn_ub' to print dn_ub.cpp, needs to be written to src/lib/x509/X509_dn_ub.cpp
        Choose 'pads' to print padding.cpp, needs to be written to src/lib/pk_pad/padding.cpp
    """
    if args is None:
        args = sys.argv
    if len(args) < 2:
        raise Exception("Use either 'oids', 'dn_ub', 'pads' as first argument")

    oid_lines = open('./src/build-data/oids.txt').readlines()

    oid_re = re.compile("^([1-9][0-9.]+) = ([A-Za-z0-9_\./\(\), -]+)(?: = )?([0-9]+)?$")
    hdr_re = re.compile("^\[([a-z0-9_]+)\]$")
    pad_re = re.compile("^([A-Za-z0-9_\., -]+)/([A-Za-z0-9_-]+)[A-Za-z0-9_\.\(\), -]*$")

    oid2str = {}
    str2oid = {}
    dn_ub = {}
    sig2pads = defaultdict(set)
    enc2pads = defaultdict(set)
    cur_hdr = None

    for line in oid_lines:
        line = line.strip()
        if len(line) == 0:
            continue

        if line[0] == '#':
            continue

        match = hdr_re.match(line)
        if match is not None:
            cur_hdr = match.group(1)
            continue

        match = oid_re.match(line)
        if match is None:
            raise Exception(line)

        oid = match.group(1)
        nam = match.group(2)

        if oid in str2oid:
            print "Duplicated OID", oid, name, oid2str[oid]
            sys.exit() # hard error
        else:
            oid2str[oid] = nam

        # parse upper bounds for DNs
        if cur_hdr == "dn":
            if match.lastindex < 3:
                raise Exception("Could not find an upper bound for DN " + match.group(1))
            dn_ub[oid] = match.group(3)
        # parse signature paddings
        elif cur_hdr == "signature":
            pad_match = pad_re.search(nam)
            if pad_match is not None:
                sig2pads[pad_match.group(1)].add(pad_match.group(2))

        if nam in str2oid:
            #print "Duplicated name", nam, oid, str2oid[nam]
            #str2oid[nam] = oid
            pass
        else:
            str2oid[nam] = oid

    if args[1] == "oids":
        print format_as_map(oid2str, str2oid)
    elif args[1] == "dn_ub":
        print format_dn_ub_as_map(dn_ub,oid2str)
    elif args[1] == "pads":
        print format_pads_as_map(sig2pads)


if __name__ == '__main__':
    sys.exit(main())
