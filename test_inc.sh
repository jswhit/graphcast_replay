charfhr2=F06
wgrib2  FV3ATM_OUTPUT_control/GFSPRS.Grb${charfhr2} -match  ":(UGRD|VGRD|TMP|HGT|SPFH):(50|100|150|200|250|300|400|500|600|700|850|925|1000) mb:" -new_grid latlon 0:1440:0.25 90:721:-0.25 GFSPRS_0p25deg.Grb${charfhr2}
wgrib2  FV3ATM_OUTPUT_control/GFSPRS.Grb${charfhr2}  -append -match "PRMSL" -new_grid latlon 0:1440:0.25 90:721:-0.25  GFSPRS_0p25deg.Grb${charfhr2}
wgrib2  FV3ATM_OUTPUT_control/GFSPRS.Grb${charfhr2}  -append -match "PRES:surface" -new_grid latlon 0:1440:0.25 90:721:-0.25 GFSPRS_0p25deg.Grb${charfhr2}
