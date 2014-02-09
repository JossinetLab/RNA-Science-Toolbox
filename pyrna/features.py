from pandas import DataFrame
import re
from bson.objectid import ObjectId
from itertools import groupby
from operator import itemgetter

class Block:
    """
    A continuous set of positions
    """
    def __init__(self, start, end):
        if start < end:
            self.start = start
            self.end = end
        else:
            self.start = end
            self.end = start

    def is_before(self, block):
        pass

    def is_beside(self, block):
        pass

    def intersects(self, block):
        pass

    def merge(self, block):
        pass


class Location:
    def __init__(self, start = None, end = None, single_positions = None):
        """
        A location can be constructed either with a start and end positions or as a list of single positions. 
        """       
        self.blocks = []
        if start and end:
            self.add_block(Block(start, end))
        elif single_positions:
            single_positions.sort()
            for k, g in groupby(enumerate(single_positions), lambda (i,x):i-x):
                _range = map(itemgetter(1), g)
                self.blocks.append(Block(min(_range), max(_range)))

    def add_block(self, block):
        blocks_to_remove = []
        
        for _block in self.blocks:
            if block.is_before(_block) and not block.is_beside(_block):
                break
            elif block.intersects(_block) or block.is_beside(_block):
                block.merge(_block)
                blocks_to_remove.append(_block)
                #its necessary to continue to see if the new Block can merge with other blocks
                continue
            elif len(blocks_to_remove):
                break
        
        for block_to_remove in blocks_to_remove:
            self.blocks.remove(block_to_remove)
        
        self.blocks.append(block)
        self.blocks = sorted(self.blocks, key=lambda block: block.start)

    def remove_location(self, location):
        """
        Return a new Location object from the difference between the current Location and the Location given as argument.
        Difference means all the positions not found in the Location given as argument
        """
        single_positions_1 = self.get_single_positions()
        single_positions_2 = location.get_single_positions()

        diff = list(set(single_positions_1) - set(single_positions_2))

        return Location(single_positions = diff)

    def remove_locations(self, locations):
        """
        Return a new Location object from the difference between the current Location with all the Locations given in a list as argument.
        Difference means all the positions not found in the Locations given as argument
        """
        single_positions_1 = self.get_single_positions()
        single_positions_2 = []

        for location in locations:
            single_positions_2 += location.get_single_positions()

        diff = list(set(single_positions_1) - set(single_positions_2))

        return Location(single_positions = diff)


    def get_single_positions(self):
        single_positions = []
        for block in self.blocks:
            single_positions += xrange(block.start, block.end+1)
        return single_positions


class Molecule:
    def __init__(self, name):
        self._id = str(ObjectId())
        self.modified_residues = []
        self.name = name
        self.family = None
        self.organism = None
        self.lineage = None
        self.source = 'N.A.:N.A.:N.A.'
        self.sequence = ""

    def get_gaps_positions(self):
        positions = []
        i = 0
        for c in list(self.sequence):
            if c == '-':
                positions.append(i)
            i += 1
        return positions

    def to_fasta(self, single_line=False):
        lines = []
        lines.append(">" + self.name)
        if single_line:
            lines.append(self.sequence)
        else:
            c = 0
            while c < len(self.sequence):
                d = min(len(self.sequence), c + 79)
                lines.append(self.sequence[c:d])
                c += 79
        return '\n'.join(lines)

    def __add__(self, seq):
        """extend the sequence of the molecule with with seq
        seq has to be a string"""
        if seq.__class__ == str:
            self.sequence = ''.join([self.sequence, seq])

    def __len__(self):
        return len(self.sequence)

    def __iter__(self):
        return iter(self.sequence)

    def __getslice__(self, i, j):
        return self.sequence.__getslice__(i, j)


class DNA(Molecule):
    def __init__(self, sequence, name = 'dna'):
        Molecule.__init__(self, name)
        self.sequence = sequence

    def get_complement(self):
        """
        Returns:
        the complement sequence as a string.
        """
        basecomplement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
        letters = list(self.sequence)
        letters = [basecomplement[base] if basecomplement.has_key(base) else base for base in letters]
        return ''.join(letters)


class RNA(Molecule):
    def __init__(self, sequence, name = 'rna'):
        Molecule.__init__(self, name)

        for residue in list(sequence):
            self.add_residue(residue)

    def add_residue(self, residue):
        if modified_ribonucleotides.has_key(residue):
            self.modified_residues.append((residue, len(self.sequence)+1))
            residue = modified_ribonucleotides[residue]
        if residue in ['A', 'U', 'G', 'C']:
            self.sequence = ''.join([self.sequence, residue])
        elif residue in ['.', '_', '-']:
            self.sequence = ''.join([self.sequence, '-'])
        else:
            #print "Unknown residue "+residue
            self.sequence = ''.join([self.sequence, residue])    

class SecondaryStructure:

    def __init__(self, rna):
        self.name = "2D"
        self.rna = rna
        self.helices = []
        self.single_strands = []
        self.tertiary_interactions = []
        self.junctions = []
        self.source = "N.A:N.A:N.A"
        self._id = str(ObjectId())

    def get_junctions(self):
        return DataFrame(self.junctions)

    def get_paired_residue(self, pos):
        for helix in self.helices:
            if pos >= helix['location'][0][0] and pos <= helix['location'][0][0] + helix['length']-1:
                return helix['location'][-1][-1] - (pos-helix['location'][0][0])
            elif pos <= helix['location'][-1][-1] and pos >= helix['location'][-1][-1] - helix['length']+1:
                return helix['location'][0][0]+ helix['location'][-1][-1] - pos
        return -1

    def find_junctions(self):
        self.junctions=[]
        for single_strand in self.single_strands:
            if single_strand['location'][0] == 1 or single_strand['location'][-1] == len (self.rna) or len(filter(lambda junction: single_strand in junction['single_strands'], self.junctions)):
                continue
            strands = [single_strand]
            descr = self.rna[single_strand['location'][0]-1:single_strand['location'][-1]]+" "
            current_pos =  self.get_paired_residue(single_strand['location'][-1]+1)+1
            crown = [[single_strand['location'][0]-1, single_strand['location'][-1]+1]] 
            next_single_strand = None           

            while current_pos >= 1 and current_pos <= len(self.rna):
                next_single_strand = filter(lambda single_strand : single_strand['location'][0] == current_pos, self.single_strands)
                if next_single_strand and next_single_strand[0] == single_strand:
                    break
                elif next_single_strand:
                    strands.append(next_single_strand[0])
                    crown.append([next_single_strand[0]['location'][0]-1, next_single_strand[0]['location'][-1]+1])
                    descr += self.rna[next_single_strand[0]['location'][0]-1:next_single_strand[0]['location'][-1]]+" "
                    current_pos = self.get_paired_residue(next_single_strand[0]['location'][-1]+1)+1
                    continue
                next_helix = filter(lambda helix: current_pos == helix['location'][0][0] or current_pos == helix['location'][-1][-1]-helix['length']+1, self.helices)
                if next_helix:
                    descr += '- '
                    crown.append([current_pos-1, current_pos])
                    current_pos = self.get_paired_residue(current_pos)+1

            if next_single_strand and next_single_strand[0] == single_strand:
                self.junctions.append({
                    'single_strands': strands,
                    'description': descr.strip(),
                    'crown': crown                    
                })

    def add_helix(self, name, start, end, length):
        helix = {
            'name': name,
            'location': [[start,start+length-1],[end-length+1,end]],
            'length': length
            }
        self.helices.append(helix)
        self.helices = sorted(self.helices, key=lambda helix: helix['location'][0][0]) #the helices are sorted according to the start position
        return helix

    def add_single_strand(self, name, start, length):
        single_strand = {
            'name': name,
            'location': [start,start+length-1]
        };
        self.single_strands.append(single_strand)
        return single_strand

    def add_tertiary_interaction(self, orientation, edge1, edge2, pos1, pos2):
        self.tertiary_interactions.append({
                            'orientation': orientation, 
                            'edge1': edge1, 
                            'edge2': edge2, 
                            'location': [[pos1, pos1], [pos2, pos2]]
                        })    

    def add_base_pair(self, orientation, edge1, edge2, pos1, pos2):
        is_secondary_interaction = False

        for helix in self.helices:
            start = helix['location'][0][0]
            end = helix['location'][-1][-1]
            length =  helix['length']

            if pos1 >= start and pos1 <= start+length-1:
                diff = pos1 -start
                if end - pos2 == diff:
                    #if not canonical (not AU, GC or GU, neither cWWW, we add it to the helix as a non-canonical secondary interaction
                    if not (self.rna.sequence[pos1-1] == 'A' and self.rna.sequence[pos2-1] == 'U' or \
                            self.rna.sequence[pos1-1] == 'U' and self.rna.sequence[pos2-1] == 'A' or \
                            self.rna.sequence[pos1-1] == 'G' and self.rna.sequence[pos2-1] == 'C' or \
                            self.rna.sequence[pos1-1] == 'C' and self.rna.sequence[pos2-1] == 'G' or \
                            self.rna.sequence[pos1-1] == 'G' and self.rna.sequence[pos2-1] == 'U' or \
                            self.rna.sequence[pos1-1] == 'U' and self.rna.sequence[pos2-1] == 'G') or \
                          orientation != 'C' or edge1 != '(' or edge2 != ')': #we have a non-canonical secondary-interaction
                        if not helix.has_key('interactions'):
                            helix['interactions'] = []
                        helix['interactions'].append({
                            'orientation': orientation, 
                            'edge1': edge1, 
                            'edge2': edge2, 
                            'location': [[pos1, pos1], [pos2, pos2]]
                        })
                    is_secondary_interaction = True
                    break

        if not is_secondary_interaction:
            #if we reach this point, its a tertiary interaction
            self.tertiary_interactions.append({
                            'orientation': orientation, 
                            'edge1': edge1, 
                            'edge2': edge2, 
                            'location': [[pos1, pos1], [pos2, pos2]]
                        })

class StructuralAlignment:

    def __init__(self, json_data):
        self.json_data = json_data

    def get_source(self):
        return self.json_data['source']

    def get_aligned_sequences(self):
        rnas = []
        for rna in self.json_data['sequences']:
            rnas.append({'name':rna['name'], 'sequence':rna['sequence']})
        return DataFrame(rnas)

    def get_consensus_2d(self):
        for interaction in self.json_data['consensus2D']:
            interaction['pos1'] = int(interaction['location']['ends'][0][0]);
            interaction['pos2'] = int(interaction['location']['ends'][1][0]);
            del(interaction['location'])    
        return DataFrame(self.json_data['consensus2D']) 


class TertiaryStructure:

    def __init__(self, rna):
        self.source = 'N.A.:N.A.:N.A.'
        self.rna = rna
        self.name = "N.A."
        self.residues = {} #the keys are the absolute position of residues
        self.numbering_system = {}
        self._id = str(ObjectId())

    def get_atoms(self):
        """
        Returns the details for atoms in a panda dataframe. Columns are:
        - atom name
        - residue absolute position
        - residue position label (according to the numbering system)
        - residue name
        - chain name
        - x (float)
        - y (float)
        - z (float)
        """
        atoms = []
        keys =[]
        for k in self.residues.keys():
            keys.append(k)

        keys.sort() #the absolute position are sorted

        for key in keys:
            atoms = self.residues[key]['atoms']
            for atom in atoms:
                atoms.append({
                    'name': atom['name'],
                    'absolute position': key,
                    'position label': self.get_residue_label(key),
                    'residue name': self.rna.sequence[key-1],
                    'chain name': self.rna.name,
                    'x': atom['coords'][0],
                    'y': atom['coords'][1],
                    'z': atom['coords'][1]
                })
        
        return DataFrame(atoms)

    def add_atom(self, atom_name, absolute_position, coords):
        atom_name = re.sub("\*", "'", atom_name)
        if atom_name == 'OP1':
            atom_name = 'O1P'
        elif atom_name == 'OP2':
            atom_name = 'O2P'
        elif atom_name == 'OP3':
            atom_name = 'O3P'
        if self.residues.has_key(absolute_position):
            self.residues[absolute_position]['atoms'].append({
                    'name': atom_name,
                    'coords': coords
                })
        else:
             self.residues[absolute_position] = {
                'atoms': [{
                    'name': atom_name,
                    'coords': coords
                }]
             }

    def get_residue_label(self, absolute_position):
        if self.numbering_system.has_key(str(absolute_position)):
            return self.numbering_system[str(absolute_position)]
        else:
            return str(absolute_position)          

modified_ribonucleotides = {
    "T": "U",
    "PSU": "U",
    "I": "A",
    "N": "U",
    "S": "U",
    "+A": "A",
    "+C": "C",
    "+G": "G",
    "+I": "I",
    "+T": "U",
    "+U": "U",
    "PU": "A",
    "YG": "G",
    "1AP": "G",
    "1MA": "A",
    "1MG": "G",
    "2DA": "A",
    "2DT": "U",
    "2MA": "A",
    "2MG": "G",
    "4SC": "C",
    "4SU": "U",
    "5IU": "U",
    "5MC": "C",
    "5MU": "U",
    "5NC": "C",
    "6MP": "A",
    "7MG": "G",
    "A23": "A",
    "AD2": "A",
    "AET": "A",
    "AMD": "A",
    "AMP": "A",
    "APN": "A",
    "ATP": "A",
    "AZT": "U",
    "CCC": "C",
    "CMP": "A",
    "CPN": "C",
    "DAD": "A",
    "DCT": "C",
    "DDG": "G",
    "DG3": "G",
    "DHU": "U",
    "DOC": "C",
    "EDA": "A",
    "G7M": "G",
    "GDP": "G",
    "GNP": "G",
    "GPN": "G",
    "GTP": "G",
    "GUN": "G",
    "H2U": "U",
    "HPA": "A",
    "IPN": "U",
    "M2G": "G",
    "MGT": "G",
    "MIA": "A",
    "OMC": "C",
    "OMG": "G",
    "OMU": "U",
    "ONE": "U",
    "P2U": "P",
    "PGP": "G",
    "PPU": "A",
    "PRN": "A",
    "PST": "U",
    "QSI": "A",
    "QUO": "G",
    "RIA": "A",
    "SAH": "A",
    "SAM": "A",
    "T23": "U",
    "T6A": "A",
    "TAF": "U",
    "TLC": "U",
    "TPN": "U",
    "TSP": "U",
    "TTP": "U",
    "UCP": "U",
    "VAA": "A",
    "YYG": "G",
    "70U": "U",
    "12A": "A",
    "2MU": "U",
    "127": "U",
    "125": "U",
    "126": "U",
    "MEP": "U",
    "TLN": "U",
    "ADP": "A",
    "TTE": "U",
    "PYO": "U",
    "SUR": "U",
    "PSD": "A",
    "S4U": "U",
    "CP1": "C",
    "TP1": "U",
    "NEA": "A",
    "GCK": "C",
    "CH": "C",
    "EDC": "G",
    "DFC": "C",
    "DFG": "G",
    "DRT": "U",
    "2AR": "A",
    "8OG": "G",
    "IG": "G",
    "IC": "C",
    "IGU": "G",
    "IMC": "C",
    "GAO": "G",
    "UAR": "U",
    "CAR": "C",
    "PPZ": "A",
    "M1G": "G",
    "ABR": "A",
    "ABS": "A",
    "S6G": "G",
    "HEU": "U",
    "P": "G",
    "DNR": "C",
    "MCY": "C",
    "TCP": "U",
    "LGP": "G",
    "GSR": "G",
    "X": "G",
    "R": "A",
    "Y": "A",
    "E": "A",
    "GSS": "G",
    "THX": "U",
    "6CT": "U",
    "TEP": "G",
    "GN7": "G",
    "FAG": "G",
    "PDU": "U",
    "MA6": "A",
    "UMP": "U",
    "SC": "C",
    "GS": "G",
    "TS": "U",
    "AS": "A",
    "ATD": "U",
    "T3P": "U",
    "5AT": "U",
    "MMT": "U",
    "SRA": "A",
    "6HG": "G",
    "6HC": "C",
    "6HT": "U",
    "6HA": "A",
    "55C": "C",
    "U8U": "U",
    "BRO": "U",
    "BRU": "U",
    "5IT": "U",
    "ADI": "A",
    "5CM": "C",
    "IMP": "G",
    "THM": "U",
    "URI": "U",
    "AMO": "A",
    "FHU": "P",
    "TSB": "A",
    "CMR": "C",
    "RMP": "A",
    "SMP": "A",
    "5HT": "U",
    "RT": "U",
    "MAD": "A",
    "OXG": "G",
    "UDP": "U",
    "6MA": "A",
    "5IC": "C",
    "SPT": "U",
    "TGP": "G",
    "BLS": "A",
    "64T": "U",
    "CB2": "C",
    "DCP": "C",
    "ANG": "G",
    "BRG": "G",
    "Z": "A",
    "AVC": "A",
    "5CG": "G",
    "UDP": "U",
    "UMS": "U",
    "BGM": "G",
    "SMT": "U",
    "DU": "U",
    "CH1": "C",
    "GH3": "G",
    "GNG": "G",
    "TFT": "U",
    "U3H": "U",
    "MRG": "G",
    "ATM": "U",
    "GOM": "A",
    "UBB": "U",
    "A66": "A",
    "T66": "U",
    "C66": "C",
    "3ME": "A",
    "A3P": "A",
    "ANP": "A",
    "FA2": "A",
    "9DG": "G",
    "GMU": "U",
    "UTP": "U",
    "5BU": "U",
    "APC": "A",
    "DI": "I",
    "UR3": "U",
    "3DA": "A",
    "DDY": "C",
    "TTD": "U",
    "TFO": "U",
    "TNV": "U",
    "MTU": "U",
    "6OG": "G",
    "E1X": "A",
    "FOX": "A",
    "CTP": "C",
    "D3T": "U",
    "TPC": "C",
    "7DA": "A",
    "7GU": "U",
    "2PR": "A",
    "CBR": "C",
    "I5C": "C",
    "5FC": "C",
    "GMS": "G",
    "2BT": "U",
    "8FG": "G",
    "MNU": "U",
    "AGS": "A",
    "NMT": "U",
    "NMS": "U",
    "UPG": "U",
    "G2P": "G",
    "2NT": "U",
    "EIT": "U",
    "TFE": "U",
    "P2T": "U",
    "2AT": "U",
    "2GT": "U",
    "2OT": "U",
    "BOE": "U",
    "SFG": "G",
    "CSL": "I",
    "PPW": "G",
    "IU": "U",
    "D5M": "A",
    "ZDU": "U",
    "DGT": "U",
    "UD5": "U",
    "S4C": "C",
    "DTP": "A",
    "5AA": "A",
    "2OP": "A",
    "PO2": "A",
    "DC": "C",
    "DA": "A",
    "LOF": "A",
    "ACA": "A",
    "BTN": "A",
    "PAE": "A",
    "SPS": "A",
    "TSE": "A",
    "A2M": "A",
    "NCO": "A",
    "A5M": "C",
    "M5M": "C",
    "S2M": "U",
    "MSP": "A",
    "P1P": "A",
    "N6G": "G",
    "MA7": "A",
    "FE2": "G",
    "AKG": "G",
    "SIN": "G",
    "PR5": "G",
    "GOL": "G",
    "XCY": "G",
    "5HU": "U",
    "CME": "C",
    "EGL": "G",
    "LC": "C",
    "LHU": "U",
    "LG": "G",
    "PUY": "U",
    "PO4": "U",
    "PQ1": "U",
    "ROB": "U",
    "O2C": "C",
    "C30": "C",
    "C31": "C",
    "C32": "C",
    "C33": "C",
    "C34": "C",
    "C35": "C",
    "C36": "C",
    "C37": "C",
    "C38": "C",
    "C39": "C",
    "C40": "C",
    "C41": "C",
    "C42": "C",
    "C43": "C",
    "C44": "C",
    "C45": "C",
    "C46": "C",
    "C47": "C",
    "C48": "C",
    "C49": "C",
    "C50": "C",
    "A30": "A",
    "A31": "A",
    "A32": "A",
    "A33": "A",
    "A34": "A",
    "A35": "A",
    "A36": "A",
    "A37": "A",
    "A38": "A",
    "A39": "A",
    "A40": "A",
    "A41": "A",
    "A42": "A",
    "A43": "A",
    "A44": "A",
    "A45": "A",
    "A46": "A",
    "A47": "A",
    "A48": "A",
    "A49": "A",
    "A50": "A",
    "G30": "G",
    "G31": "G",
    "G32": "G",
    "G33": "G",
    "G34": "G",
    "G35": "G",
    "G36": "G",
    "G37": "G",
    "G38": "G",
    "G39": "G",
    "G40": "G",
    "G41": "G",
    "G42": "G",
    "G43": "G",
    "G44": "G",
    "G45": "G",
    "G46": "G",
    "G47": "G",
    "G48": "G",
    "G49": "G",
    "G50": "G",
    "T30": "U",
    "T31": "U",
    "T32": "U",
    "T33": "U",
    "T34": "U",
    "T35": "U",
    "T36": "U",
    "T37": "U",
    "T38": "U",
    "T39": "U",
    "T40": "U",
    "T41": "U",
    "T42": "U",
    "T43": "U",
    "T44": "U",
    "T45": "U",
    "T46": "U",
    "T47": "U",
    "T48": "U",
    "T49": "U",
    "T50": "U",
    "U30": "U",
    "U31": "U",
    "U32": "U",
    "U33": "U",
    "U34": "U",
    "U35": "U",
    "U36": "U",
    "U37": "U",
    "U38": "U",
    "U39": "U",
    "U40": "U",
    "U41": "U",
    "U42": "U",
    "U43": "U",
    "U44": "U",
    "U45": "U",
    "U46": "U",
    "U47": "U",
    "U48": "U",
    "U49": "U",
    "U50": "U",
    "UFP": "U",
    "UFR": "U",
    "UCL": "U",
    "3DR": "U",
    "CBV": "C",
    "HFA": "A",
    "MMA": "A",
    "DCZ": "C",
    "GNE": "C",
    "A1P": "A",
    "6IA": "A",
    "CTG": "G",
    "5FU": "U",
    "2AD": "A",
    "T2T": "U",
    "XUG": "G",
    "2ST": "U",
    "5PY": "U",
    "4PC": "C",
    "US1": "U",
    "M5C": "C",
    "DG": "G",
    "DA": "A",
    "DT": "U",
    "DC": "C",
    "P5P": "A",
    "FMU": "U"
}