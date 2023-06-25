"""
Create a json file for displaying family as a javascript sunburst.
Requires use of an associated javascript library and d3.js

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2023 John A. Andrea
v0.2

No support provided.
"""

import sys
import importlib.util
import argparse
import re
import os

DEFAULT_COLOR = '#e0f3f8'  #level missing or out of range, bluish
# colors from d3 RdYlGn
LEVEL_COLORS = {'0':'#a50026', # unidentified ancestor, redish
                '1':'#d73027', # names only, redorangish
                '2':'#f46d43', # vital stats, lighter red
                '3':'#fdae61', # occ, residence, children, spouses, orangish
                '4':'#fee08b', # property, military service, yellowish
                '5':'#a6d96a', # genealogical proof standard, light greenish
                '6':'#1a9850'  # biography, greenish
               }

PLAIN_COLORS = ['#E5D8BD', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3', '#FDB462',
                '#B3DE69', '#FCCDE5', '#D9D9D9', '#BC80BD', '#CCEBC5', '#FFED6F',
                '#E5C494', '#BCBD22', '#CCEBC5' ]

n_plain_colors = len( PLAIN_COLORS ) - 1
color_index = 0 # or should it be random to start

GENDER_COLORS = {'f':'#FB8072', 'm':'#80B1D3', 'x':'#FFFFB3'}


def load_my_module( module_name, relative_path ):
    """
    Load a module in my own single .py file. Requires Python 3.6+
    Give the name of the module, not the file name.
    Give the path to the module relative to the calling program.
    Requires:
        import importlib.util
        import os
    Use like this:
        readgedcom = load_my_module( 'readgedcom', '../libs' )
        data = readgedcom.read_file( input-file )
    """
    assert isinstance( module_name, str ), 'Non-string passed as module name'
    assert isinstance( relative_path, str ), 'Non-string passed as relative path'

    file_path = os.path.dirname( os.path.realpath( __file__ ) )
    file_path += os.path.sep + relative_path
    file_path += os.path.sep + module_name + '.py'

    assert os.path.isfile( file_path ), 'Module file not found at ' + str(file_path)

    module_spec = importlib.util.spec_from_file_location( module_name, file_path )
    my_module = importlib.util.module_from_spec( module_spec )
    module_spec.loader.exec_module( my_module )

    return my_module


def get_program_options():
    results = dict()

    directions = [ 'desc', 'descendant', 'descendants', 'descendent', 'descendents',
                   'anc', 'ancestor', 'ancestors' ]
    schemes = [ 'plain', 'gender', 'level' ]

    results['infile'] = None
    results['start_person'] = None
    results['levels_tag'] = None

    results['scheme'] = schemes[0]
    results['direction'] = directions[0]
    results['dates'] = False
    results['id_item'] = 'xref'

    results['libpath'] = '.'

    arg_help = 'Produce a JSON file for Javascript sunburst display.'
    parser = argparse.ArgumentParser( description=arg_help )

    arg_help = 'Color scheme. Plain or gender. Default: ' + results['scheme']
    parser.add_argument( '--scheme', default=results['scheme'], type=str, help=arg_help )

    arg_help = 'Direction of the tree from the start person. Ancestors or descendants.'
    arg_help += ' Default:' + results['direction']
    parser.add_argument( '--direction', default=results['direction'], type=str, help=arg_help )

    arg_help = 'Show dates along with the names.'
    parser.add_argument( '--dates', default=results['dates'], action='store_true', help=arg_help )

    arg_help = 'How to find the person in the input. Default is the gedcom id "xref".'
    arg_help += ' Othewise choose "type.exid", "type.refnum", etc.'
    parser.add_argument( '--id_item', default=results['id_item'], type=str, help=arg_help )

    # maybe this should be changed to have a type which better matched a directory
    arg_help = 'Location of the gedcom library. Default is current directory.'
    parser.add_argument( '--libpath', default=results['libpath'], type=str, help=arg_help )

    parser.add_argument( 'infile', type=argparse.FileType('r'), help='input GEDCOM file' )
    parser.add_argument( 'start_person', help='Id of person at the center of the display' )
    parser.add_argument( 'levels_tag', nargs='?', help='Tag which holds the levels value. Optional' )

    args = parser.parse_args()

    results['infile'] = args.infile.name
    results['start_person'] = args.start_person.lower().strip()

    # optional
    if args.levels_tag:
       results['levels_tag'] = args.levels_tag.strip()

    results['dates'] = args.dates
    results['id_item'] = args.id_item.lower().strip()
    results['libpath'] = args.libpath

    value = args.direction.lower()
    if value.startswith('anc'):
       results['direction'] = 'anc'

    value = args.scheme.lower()
    if value in schemes:
       results['scheme'] = value

    return results


def looks_like_int( s ):
    return re.match( r'\d\d*$', s )


def fix_names( s ):
    # can't handle "[ em|ndash ? em|ndash ]"
    return s.replace( '—', '-' )


def get_name_parts( indi ):
    name = fix_names( data[i_key][indi]['name'][0]['unicode'] )
    names = name.split()
    first = names[0]
    if add_dates:
       name += '\\ndates'
    return [ name, first ]


def get_levels_color( indi_data ):
    global levels_tag
    result = DEFAULT_COLOR
    if 'even' in indi_data:
       for event in indi_data['even']:
           if levels_tag == event['type']:
              result = LEVEL_COLORS.get( event['value'], DEFAULT_COLOR )
    return result


def compute_color( gender_guess, indi ):
    global color_index

    result = PLAIN_COLORS[color_index]
    color_index = ( color_index + 1 ) % n_plain_colors

    if use_gender:
       gender = 'x'
       if 'sex' in data[i_key][indi]:
          sex = data[i_key][indi]['sex'][0].lower()
          if sex in ['m','f']:
             gender = sex
       else:
          if gender_guess == 'wife':
             gender = 'f'
          if gender_guess == 'husb':
             gender = 'm'
       result = GENDER_COLORS[gender]

    else:
       if use_levels:
         result = get_levels_color( data[i_key][indi] )

    return result


def get_parents( fam ):
    result = ''
    space = ''
    for parent in ['husb','wife']:
        if parent in data[f_key][fam]:
           parent_id = data[f_key][fam][parent][0]
           if parent_id is not None:
              name_parts = get_name_parts( parent_id )
              result += space + name_parts[0]
              space = '\\n+ '
    return result


def print_key_value( leadin, key, value ):
    print( leadin + '"' + key + '":"' + value + '"', end='' )


def ancestors( indi, color, needs_comma, indent ):
    stats = dict()
    stats['n'] = 1

    if use_levels:
       stats['missing'] = 0
       stats['out-of-range'] = 0
       for level_color in LEVEL_COLORS:
           stats[level_color] = 0

    if needs_comma:
       print( ',' )

    name_parts = get_name_parts( indi )
    detail = name_parts[0]
    first = name_parts[1]

    print( indent, end='' )
    print_key_value( '{', 'name', first )
    print_key_value( ', ', 'detail', detail )
    print_key_value( ', ', 'color', color )

    # assume only biological relationships
    if 'famc' in data[i_key][indi]:
       fam = data[i_key][indi]['famc'][0]

       # these are the person's parents, but the drawing code needs tree node "children"
       print( ', "children": [' )

       add_comma = False
       for partner_type in ['wife','husb']:
           if partner_type in data[f_key][fam]:
              partner = data[f_key][fam][partner_type][0]
              new_stats = ancestors( partner, compute_color(partner_type,partner), add_comma, indent + '  ' )
              add_comma = True

              for item in new_stats:
                  stats[item] += new_stats[item]

       print( '\n', indent, ']}', end='' )

    else:
       print( ', "size": 1 }', end='' )

    return stats


def descendants( indi, color, needs_comma, indent, parents ):
    stats = dict()
    stats['n'] = 1
    stats = dict()

    if use_levels:
       stats['missing'] = 0
       stats['out-of-range'] = 0
       for level_color in LEVEL_COLORS:
           stats[level_color] = 0

    if needs_comma:
       print( ',' )

    name_parts = get_name_parts( indi )
    detail = name_parts[0]
    first = name_parts[1]

    if parents:
       detail += '\\nParents:\\n' + parents

    print( indent, end='' )
    print_key_value( '{', 'name', first )
    print_key_value( ', ', 'detail', detail )
    print_key_value( ', ', 'color', color )

    n_children = 0
    needs_comma = False

    if 'fams' in data[i_key][indi]:
       for fam in data[i_key][indi]['fams']:
           parent_info = get_parents( fam )
           if 'chil' in data[f_key][fam]:
              for child in data[f_key][fam]['chil']:
                  n_children += 1

                  if n_children == 1:
                     print( ', "children": [' )
                  new_stats = descendants( child, compute_color('x',child), needs_comma, indent + '  ', parent_info )
                  needs_comma = True

    if n_children > 0:
       print( '\n', indent, ']}', end='' )
    else:
       print( ', "size": 1 }', end='' )

    return stats


use_levels = False
use_gender = False
levels_tag = None
add_dates = False

options = get_program_options()
print( options, file=sys.stderr ) #debug

if options['scheme'] == 'gender':
   use_gender = True
if options['levels_tag']:
   use_gender = False
   use_levels = True
   levels_tag = options['levels_tag']
add_dates = options['dates']

readgedcom = load_my_module( 'readgedcom', options['libpath'] )

read_opts = dict()
read_opts['display-gedcom-warnings'] = False

data = readgedcom.read_file( options['infile'], read_opts )

i_key = readgedcom.PARSED_INDI
f_key = readgedcom.PARSED_FAM

start_ids = readgedcom.find_individuals( data, options['id_item'], options['start_person'] )

if len(start_ids) < 1:
   print( 'Did not find start person:', options['start_person'], 'with', options['id_item'], file=sys.stderr )
   sys.exit(1)
if len(start_ids) > 1:
   print( 'More than one id for start person:', options['start_person'], 'with', options['id_item'], file=sys.stderr )
   sys.exit(1)

print( 'Starting with', get_name_parts( start_ids[0] )[0], file=sys.stderr )

stats = []
if options['direction'] == 'anc':
   stats = ancestors( start_ids[0], compute_color( 'x', start_ids[0] ), False, '' )
else:
   stats = descendants( start_ids[0], compute_color( 'x', start_ids[0] ), False, '', '' )

print( stats, file=sys.stderr )
