select species, the_geom, rangemap_inside(species, the_geom) from gbif_sep2014 where the_geom is not null and species='Puma concolor' limit 10;
