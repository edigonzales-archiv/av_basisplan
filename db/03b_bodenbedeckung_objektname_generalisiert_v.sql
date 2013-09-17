-- View: av_basisplan.bodenbedeckung_objektname_generalisiert_v

-- DROP VIEW av_basisplan.bodenbedeckung_objektname_generalisiert_v;

CREATE OR REPLACE VIEW av_basisplan.bodenbedeckung_objektname_generalisiert_v AS 
 SELECT bodenbedeckung_objektname_v.ogc_fid, bodenbedeckung_objektname_v.tid, bodenbedeckung_objektname_v.objektnamepos_von, bodenbedeckung_objektname_v.pos, bodenbedeckung_objektname_v.ori, bodenbedeckung_objektname_v.rot, bodenbedeckung_objektname_v.hali_txt, bodenbedeckung_objektname_v.vali_txt, bodenbedeckung_objektname_v.groesse_txt, bodenbedeckung_objektname_v.gem_bfs, bodenbedeckung_objektname_v.los, bodenbedeckung_objektname_v.lieferdatum, bodenbedeckung_objektname_v.name, bodenbedeckung_objektname_v.art_txt, bodenbedeckung_objektname_v.xlabel, bodenbedeckung_objektname_v.ylabel, bodenbedeckung_objektname_v.area
   FROM av_basisplan.bodenbedeckung_objektname_v
  WHERE (bodenbedeckung_objektname_v.ogc_fid IN ( SELECT DISTINCT ON (st_x(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision)), st_y(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision))) bodenbedeckung_objektname_v.ogc_fid
           FROM av_basisplan.bodenbedeckung_objektname_v
          ORDER BY st_x(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision)), st_y(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision)), st_distance(bodenbedeckung_objektname_v.pos, st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision))));

ALTER TABLE av_basisplan.bodenbedeckung_objektname_generalisiert_v OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.bodenbedeckung_objektname_generalisiert_v TO stefan;
GRANT SELECT ON TABLE av_basisplan.bodenbedeckung_objektname_generalisiert_v TO stefan;

