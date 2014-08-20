"""latexout.py

Module for saving all the information about a StarSystem to a LaTeX file for
processing towards a nicely formatted PDF file.
"""

#from ..starsystem import StarSystem
from ..tables import AtmCompAbbr

class LatexWriter:
    def __init__(self, starsystem, filename='starsystem.tex'):
        self.starsystem = starsystem
        self.filename = filename

    def write(self):
        # Open the file
        file = open(self.filename, 'w')

        # Write the preamble
        file.write(self.preamble())

        # Write the title page, ToC and first chapter
        file.write(self.title())

        # Write stellar system and star properties
        file.write(self.starsystemprop())

        file.write(self.starprop())

        # Write the overviews
        file.write(self.overviews())

        # Write the end of document
        file.write(self.end())
        # Close the file
        file.close()

    def preamble(self):
        preambulum = """\documentclass[a4paper,12pt,twoside]{scrreprt}

\\usepackage[T1]{fontenc}
\\usepackage[latin1]{inputenc}
\\usepackage[inner=35mm,outer=25mm,top=30mm,bottom=30mm]{geometry}
\\usepackage{float}
\\usepackage[hidelinks]{hyperref}
\\usepackage{booktabs}
\\usepackage{multirow}
\\usepackage[figuresright]{rotating} % For sideways tables
\\usepackage{pdflscape} % For rotation in the PDF
\setkomafont{sectioning}{\\bfseries}

% Activate the following two for nicer fonts
%\\usepackage{charter}
%\\usepackage[bitstream-charter]{mathdesign}

\\usepackage{scrlayer-scrpage}
\pagestyle{scrheadings}

\setcounter{tocdepth}{1}

"""
        return preambulum

    def title(self):
        titelus = """
\\begin{document}
\\title{CAS: Computer-Assisted Starsystem}
\subtitle{A GURPS Star System}
\\author{The Guy in Front of The Computer}
\date{\\today}
\maketitle

\\tableofcontents
\clearpage

\chapter{Summary}
\section{General Description}
% Give a general description, such as the one you could hand out to your players

\section{GM Notes}
% Enter here the GM Notes

"""
        return titelus

    def starsystemprop(self):
        str = """\chapter{The Star System}
\section{Star System Properties}
"""
        numstar = len(self.starsystem.stars)
        str += "Number of stars: {}\\\\ \n".format(numstar)
        age = self.starsystem.getAge()
        str += "Stellar age: {} billion years \n\n".format(age)

        # Only put table (about the properties of the stellar system) if
        # necessary (i.e. more than one star)
        if numstar > 1:
            str += """\\begin{table}[H]
\centering
\\begin{tabular}{"""
            str += 'l' * numstar
            str += "}\n\\toprule \n"
            if numstar == 2:
                header = "Pair A--B \\\\ \n"
            else:
                header = "Pair A--B & Pair A--C \\\\ \n"
            str += "Property & " + header
            str += "\midrule\n"
            # Extract orbit and eccentricities
            oecc = self.starsystem.getOrbits()
            orb = ''
            ecc = ''
            for o, e in oecc:
                orb += ' & {:8.2f}'.format(round(o, 2))
                ecc += ' & {:8.2f}'.format(round(e, 2))
            str += "Orbital Separation [AU] " + orb + ' \\\\ \n'
            str += "Orbital Eccentricity    " + ecc + ' \\\\ \n'
            str += "Orbital Period [d]      "
            for per in self.starsystem.getPeriod():
                str += ' & {:7.1f} '.format(round(per, 1))
            str += " \\\\ \n"
            str += "\\bottomrule\n\end{tabular} \n\end{table}\n\n"
        return str

    def starprop(self):
        str = """\section{Star Properties}
% Number of data columns = Number of stars
\\begin{table}[H]
\centering
\\begin{tabular}{"""
        numstar = len(self.starsystem.stars)
        str += 'l' * (numstar + 1) + '}\n'
        str += '\\toprule\n'
        str += 'Property '
        letters = ['A', 'B', 'C']
        for nst in range(numstar):
            str += '& Star ' + letters[nst] + ' '
        str += '\\\\ \n\midrule\n'

        sequence = 'Sequence   '
        mass = 'Mass       '
        temp = 'Temperature'
        lum = 'Luminosity '
        rad = 'Radius     '
        inner = 'Inner Limit'
        outer = 'Outer Limit'
        snowline = 'Snow line  '
        if numstar > 1:
            fzinner = 'FZ Inner   '
            fzouter = 'FZ Outer   '
        for star in self.starsystem.stars:
            sequence += ' & ' + star.getSequence()
            mass += ' & {:7.2f}'.format(star.getMass())
            temp += ' & {:7.0f}'.format(star.getTemp())
            lum += ' & {:7.4f}'.format(star.getLuminosity())
            rad += ' & {:7.5f}'.format(star.getRadius())
            inner += ' & {:7.2f}'.format(star.getOrbitlimits()[0])
            outer += ' & {:6.1f} '.format(star.getOrbitlimits()[1])
            snowline += ' & {:7.2f}'.format(star.getSnowline())
            if numstar > 1:
                fzinner += ' & {:6.1f} '.format(star.getForbidden()[0])
                fzouter += ' & {:6.1f} '.format(star.getForbidden()[1])
        #for string in [sequence, mass, temp, lum, rad, inner, outer, snowline]:
        #    string += '\\\\ \n'
        eol = ' \\\\ \n'
        sequence += eol
        mass += eol
        temp += eol
        lum += eol
        rad += eol
        inner += eol
        outer += eol
        snowline += eol
        if numstar > 1:
            fzinner += eol
            fzouter += eol

        str += sequence + mass + temp + lum + rad + inner + outer + snowline
        if numstar > 1:
            str += fzinner + fzouter
        str += '\\bottomrule\n\end{tabular} \n\end{table} \n\n'

        return str


    def overviews(self):
        # Gather number of planet systems
        # For each planet system:
        #  - List orbits and occupants
        #  - List terrestrial planet details
        #  - List Moons and Moonlets
        #  - List Asteroid Belts
        str = ''
        letters = ['A', 'B', 'C']
        for star in self.starsystem.stars:
            idx = self.starsystem.stars.index(star)
            lettr = letters[idx]
            ps = star.planetsystem
            oc = ps.getOrbitcontents()
            types = [pl.type() for key, pl in oc.items()]

            title = 'Overview -- Planet System ' + lettr
            str += '\chapter{' + title + '}\n'
            str += '\section{Summary}\n% A small amount of short sentences describing the general feel of this planet system.\n\n'
            str += '\section{Description}\n% A more in-depth description of the planet system.\n\n'
            str += '\section{GM Notes}\n% Notes about the planet system and eventual adventures that can be undertaken.\n\n'
            str += '\\begin{landscape}\n\section{List of Orbits and their Occupants}\n\\begin{table}[H]\n\\begin{tabular}{llllrrrrrrrrr}\n'
            str += '\\toprule\n'
            str += '\multirow{2}{*}{Name} & \multirow{2}{*}{Type} & \multirow{2}{*}{Size} & \multirow{2}{*}{World} & $R_\mathrm{orb}$ & $P_\mathrm{orb}$ & \multirow{2}{*}{Ecc.} & $R_\mathrm{min}$ & $R_\mathrm{max}$ & \multirow{2}{*}{Moons} & \multirow{2}{*}{Moonlets} & $T_\mathrm{BB}$ \\\\ \n'
            str += '\cmidrule(lr){5-5} \cmidrule(lr){6-6} \cmidrule(lr){8-8} \cmidrule(lr){9-9} \cmidrule(lr){12-12}\n'
            str += '& & & & \multicolumn{1}{c}{AU} & \multicolumn{1}{c}{Year} & & \multicolumn{1}{c}{AU} & \multicolumn{1}{c}{AU} & & & \multicolumn{1}{c}{K} \\\\ \n'
            str += '\midrule\n'
            planetcounter = 0
            for skey in sorted(oc):
                planetcounter += 1
                str += '<{}-{}> & '.format(lettr, planetcounter)
                str += '{} & '.format(oc[skey].type())
                str += '{} & '.format(oc[skey].getSize())
                str += '{} & '.format(oc[skey].getType())
                str += '{:.2f} & '.format(oc[skey].getOrbit())
                str += '{:.2f} & '.format(oc[skey].getPeriod())
                str += '{:.2f} & '.format(oc[skey].getEcc())
                str += '{:.2f} & '.format(oc[skey].getMinMax()[0])
                str += '{:.2f} & '.format(oc[skey].getMinMax()[1])
                nmoon = oc[skey].numMoons()
                nmoonlts = oc[skey].numMoonlets()
                if nmoon is 0:
                    str += ' & '
                else:
                    str += '{} & '.format(oc[skey].numMoons())
                if nmoonlts is 0:
                    str += ' & '
                else:
                    str += '{} & '.format(oc[skey].numMoonlets())
                str += '{:.0f}'.format(oc[skey].getBBTemp())
                str += '\\\\ \n'
            str += '\\bottomrule\n\end{tabular}\n\end{table}\n\n'

            # Now gather all asteroid belts and print an overview table
            astable = '\section{List of Asteroid Belts}\n\n'
            astable += '\\begin{table}[H]\n\\begin{tabular}{lrlrrr}\n'
            astable += '\\toprule\n'
            astable += 'Name & $T_\mathrm{surf}$ [K] & Climate Type & RVM & Affinity \\\\ \n'
            astable += '\midrule\n'
            planetcounter = 0
            for skey in sorted(oc):
                planetcounter += 1
                if oc[skey].type() != 'Ast. Belt':
                    continue
                astable += '<{}-{}> & '.format(lettr, planetcounter)
                astable += '{:.0f} & '.format(oc[skey].getAvSurf())
                astable += '{} & '.format(oc[skey].getClimate())
                astable += '{:+.0f} & '.format(oc[skey].getRVM())
                astable += '{:+.0f} '.format(oc[skey].getAffinity())
                astable += '\\\\ \n'
            astable += '\\bottomrule\n\end{tabular}\n\end{table}\n\n'

            if 'Ast. Belt' in types:
                str += astable
            else:
                str += '\pagebreak\n\n'

            # Make a detail table for all terrestrials
            tertable = '\section{List of Planets and their Properties}\n'
            tertable += '\\begin{table}[H]\n\\begin{tabular}{l ' + ('l' * types.count('Terrestrial')) + '}\n'
            tertable += '\\toprule\n'
            planetcounter = 0
            tertable += '\multirow{2}{*}{Property} & \multicolumn{' + '{}'.format(types.count('Terrestrial')) + '}{c}{Planet Name}\\\\ \n'
            for skey in sorted(oc):
                planetcounter += 1
                if oc[skey].type() != 'Terrestrial':
                    continue
                tertable += ' & <{}-{}>'.format(lettr, planetcounter)
            tertable += '\\\\ \n\midrule\n'
            wtype = 'World Type'
            size = 'World Size'
            atmass = 'Atm. Mass'
            atcom = 'Atm. Comp.$^1$'
            hydro = 'Hydr. Cov. [\%]'
            tsurf = '$T_\mathrm{surf}$ [K]'
            climate = 'Climate Type'
            dens = 'Density'
            diam = 'Diameter'
            grav = 'Surface Gravity'
            mass = 'Mass'
            press = 'Pressure [atm]'
            presscat = 'Pressure Cat.'
            tte = 'TTE$^2$'
            volc = 'Volcanics'
            tect = 'Tectonics'
            rvm = 'RVM$^3$'
            hab = 'Habitability'
            aff = 'Affinity'
            prot = '$P_\mathrm{rot}$ [d]'
            axtilt = 'Axial Tilt [$^\circ$]'
            for skey in sorted(oc):
                if oc[skey].type() != 'Terrestrial':
                    continue
                wtype += ' & {}'.format(oc[skey].getType())
                size += ' & {}'.format(oc[skey].getSize())
                if oc[skey].getAtmass() == 0:
                    atmass += ' & '
                    atcom += ' & '
                    press += ' & '
                else:
                    atmass += ' & {}'.format(oc[skey].getAtmass())
                    atcom += ' & '
                    atcomp = oc[skey].atmcomp
                    atkeys = [key for key in atcomp.keys() if atcomp[key] == True]
                    abbr = ''
                    for k in atkeys:
                        abbr += AtmCompAbbr[k] + ', '
                    atcom += abbr[:-2]
                    press += ' & {:.3f}'.format(oc[skey].getPressure())
                if oc[skey].getHydrocover() == 0:
                    hydro += ' & '
                else:
                    hydro += ' & {}'.format(oc[skey].getHydrocover())
                tsurf += ' & {:.0f}'.format(oc[skey].getAvSurf())
                climate += ' & {}'.format(oc[skey].getClimate())
                axtilt += ' & {}'.format(oc[skey].getAxialTilt())
                dens += ' & {}'.format(oc[skey].getDensity())
                diam += ' & {:.2f}'.format(oc[skey].getDiameter())
                grav += ' & {:.2f}'.format(oc[skey].getGravity())
                mass += ' & {:.3f}'.format(oc[skey].getMass())
                presscat += ' & {}'.format(oc[skey].getPressCat())
                tte += ' & {:.0f}'.format(oc[skey].getTTE())
                volc += ' & {}'.format(oc[skey].getVolcanism())
                tect += ' & {}'.format(oc[skey].getTectonics())
                rvm += ' & {:+.0f}'.format(oc[skey].getRVM())
                hab += ' & {:+.0f}'.format(oc[skey].getHabitability())
                aff += ' & {:+.0f}'.format(oc[skey].getAffinity())
                prot += ' & {:.2f}'.format(oc[skey].getRotation())
            lend = '\\\\ \n'
            tertable += size + lend
            tertable += wtype + lend
            tertable += atmass + lend
            tertable += atcom + lend
            tertable += hydro + lend
            tertable += tsurf + lend
            tertable += climate + lend
            tertable += axtilt + lend
            tertable += dens + lend
            tertable += diam + lend
            tertable += grav + lend
            tertable += mass + lend
            tertable += press + lend
            tertable += presscat + lend
            tertable += tte + lend
            tertable += volc + lend
            tertable += tect + lend
            tertable += rvm + lend + hab + lend + aff + lend
            tertable += prot + lend
            tertable += '\\bottomrule\n\end{tabular}\n\n'
            tertable += '\\footnotesize\n$^1$ '
            tertable += '\\textbf{C}: Corrosive, \\textbf{LT}: Lethally Toxic, \\textbf{HT}: Highly Toxic, \\textbf{MT}: Mildly Toxic, \\textbf{S}: Suffocating\\\\ \n'
            tertable += '$^2$ Total Tidal Effect\\\\ \n'
            tertable += '$^3$ Resource Value Modifier \n'
            tertable += '\end{table}\n\n'
            if 'Terrestrial' in types:
                str += tertable
            del tertable




            str += '\end{landscape}\n\n'
        return str


    def end(self):
        return "\n\n\\end{document}"
