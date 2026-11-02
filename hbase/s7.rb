count 'hotspot'
get 'hotspot', 'g088110#79739076#1834#39858'
scan 'hotspot', {STARTROW => 'g087112#', STOPROW => 'g087112$'}
scan 'hotspot', {FILTER => "ValueFilter(=, 'binary:63.86')"}

exit
