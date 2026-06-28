from tabulate import tabulate


flavor_values = []

def getNumber (message):
    print('')
    while True:
        print(message)
        output = input('> ')
        if output == '':
            output = 0
        try:
            return float(output)
        except ValueError:
            print('Error: bad value entered. Please enter a number (integer or float)')

def getFlavorName ():
    print('')
    global flavor_values
    if flavor_values:
        print(f'Current flavor quantity: {len(flavor_values)}')
    print('Flavor name (leave blank to stop adding flavors)')
    return input('> ')

class Fluid:
    def __init__ (self, volume=0, pg_pct=0, vg_pct=0, nicPerML=0):
        self.volume = volume
        global target_volume
        self.batch_pct = round(self.volume / target_volume * 100, 1)
        self.nicPerML = nicPerML

        self.pg_pct = pg_pct
        self.pg_volume = self.volume * (pg_pct / 100)
        self.pg_weight = round(self.pg_volume * 1.036, 1)

        self.vg_pct = vg_pct
        self.vg_volume = self.volume * (vg_pct / 100)
        self.vg_weight = round(self.vg_volume * 1.261, 1)

    @property
    def weight (self):
        # Note : this only accounts for PG & VG weights, not other additives. Close enough for practical purposes & non-industrial batches.
        return self.pg_weight + self.vg_weight

# ----------------------------------------------------------------------------------------------------------------------
# ----- Batch ----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

target_volume = getNumber('Target batch volume (milliliters)')
target_nicMG = getNumber('Target nicotine strength (milligrams)')
target_PGpct = getNumber('Target PG percentage')
target_VGpct = getNumber('Target VG percentage')

# ----------------------------------------------------------------------------------------------------------------------
# ----- Nicotine -------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

nic_MGperML = getNumber('Nicotine concentrate strength (milligrams per milliliter')
nic_PGpct = getNumber('Nicotine concentrate PG percentage')
nic_VGpct = getNumber('Nicotine concentrate VG percentage')

nic = Fluid(pg_pct = nic_PGpct, vg_pct = nic_VGpct, nicPerML = nic_MGperML,
            volume = round(target_volume / nic_MGperML * target_nicMG, 1))

# ----------------------------------------------------------------------------------------------------------------------
# ----- Flavor ---------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

while True:
    name = getFlavorName()
    if not name:
        break
    flavor_pct = getNumber(f'{name} percentage of total volume')
    flavor_pg = getNumber(f'{name} PG percentage')
    flavor_vg = getNumber(f'{name} VG percentage')
    flavor_values.append(Fluid(volume=(target_volume*(flavor_pct/100)),
                               pg_pct=flavor_pg, vg_pct=flavor_vg))
    flavor_values[-1].name = name


# ----------------------------------------------------------------------------------------------------------------------
# ----- Base -----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

current_volume = nic.volume
current_pg_volume = nic.pg_volume
current_vg_volume = nic.vg_volume
for flavor in flavor_values:
    current_volume += flavor.volume
    current_pg_volume += flavor.pg_volume
    current_vg_volume += flavor.vg_volume

pg = Fluid(volume = target_volume * (target_PGpct / 100) - current_pg_volume, pg_pct = 100)
vg = Fluid(volume = target_volume * (target_VGpct / 100) - current_vg_volume, vg_pct = 100)

# ----------------------------------------------------------------------------------------------------------------------
# ----- Recipie --------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

headers = ('Fluid', 'ml', 'grams', '%')
table = [('Nicotine', nic.volume, nic.weight, nic.batch_pct)]
for flavor in flavor_values:
    table.append((flavor.name, flavor.volume, flavor.weight, flavor.batch_pct))
table.append(('PG Base', pg.volume, pg.weight, pg.batch_pct))
table.append(('VG Base', vg.volume, vg.weight, vg.batch_pct))

final_weight = 0
for fluid in table:
    final_weight += fluid[2]

table.append(('','','',''))
table.append(('Total', target_volume, final_weight))

print(tabulate(table, headers, tablefmt='rounded_outline'))