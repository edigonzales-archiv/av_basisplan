-- DROP VIEW av_basisplan.einzelobjekte_flaechenelement_v;

CREATE OR REPLACE VIEW av_basisplan.einzelobjekte_flaechenelement_v AS 
 SELECT fe.ogc_fid, fe.tid, fe.flaechenelement_von, fe.geometrie, fe.gem_bfs, fe.los, fe.lieferdatum, eo.art, eo.art_txt
   FROM av_avdpool_ch.einzelobjekte_einzelobjekt eo, av_avdpool_ch.einzelobjekte_flaechenelement fe
  WHERE fe.flaechenelement_von::text = eo.tid::text;

ALTER TABLE av_basisplan.einzelobjekte_flaechenelement_v OWNER TO bpadmin;
GRANT ALL ON TABLE av_basisplan.einzelobjekte_flaechenelement_v TO bpadmin;
GRANT SELECT ON TABLE av_basisplan.einzelobjekte_flaechenelement_v TO mspublic;


-- DROP VIEW av_basisplan.einzelobjekte_linienelement_v;

CREATE OR REPLACE VIEW av_basisplan.einzelobjekte_linienelement_v AS 
 SELECT le.ogc_fid, le.tid, le.linienelement_von, le.geometrie, le.gem_bfs, le.los, le.lieferdatum, eo.art, eo.art_txt
   FROM av_avdpool_ch.einzelobjekte_einzelobjekt eo, av_avdpool_ch.einzelobjekte_linienelement le
  WHERE le.linienelement_von::text = eo.tid::text;

ALTER TABLE av_basisplan.einzelobjekte_linienelement_v OWNER TO bpadmin;
GRANT ALL ON TABLE av_basisplan.einzelobjekte_linienelement_v TO bpadmin;
GRANT SELECT ON TABLE av_basisplan.einzelobjekte_linienelement_v TO mspublic;


-- DROP VIEW av_basisplan.einzelobjekte_punktelement_v;

CREATE OR REPLACE VIEW av_basisplan.einzelobjekte_punktelement_v AS 
 SELECT pe.ogc_fid, pe.tid, pe.punktelement_von, pe.geometrie, pe.ori, pe.gem_bfs, pe.los, pe.lieferdatum, eo.art, eo.art_txt
   FROM av_avdpool_ch.einzelobjekte_einzelobjekt eo, av_avdpool_ch.einzelobjekte_punktelement pe
  WHERE pe.punktelement_von::text = eo.tid::text;

ALTER TABLE av_basisplan.einzelobjekte_punktelement_v OWNER TO bpadmin;
GRANT ALL ON TABLE av_basisplan.einzelobjekte_punktelement_v TO bpadmin;
GRANT SELECT ON TABLE av_basisplan.einzelobjekte_punktelement_v TO mspublic;


-- DROP VIEW av_basisplan.bodenbedeckung_objektname_v;

CREATE OR REPLACE VIEW av_basisplan.bodenbedeckung_objektname_v AS 
 SELECT pos.ogc_fid, pos.tid, pos.objektnamepos_von, pos.pos, pos.ori, 
        CASE
            WHEN pos.ori IS NULL THEN 0::double precision
            ELSE (100::double precision - pos.ori) * 0.9::double precision
        END AS rot, pos.hali_txt, pos.vali_txt, pos.groesse_txt, pos.gem_bfs, pos.los, pos.lieferdatum, oname.name, boflaeche.art_txt, st_x(pos.pos) AS xlabel, st_y(pos.pos) AS ylabel, st_area(boflaeche.geometrie) AS area
   FROM av_avdpool_ch.bodenbedeckung_objektnamepos pos, av_avdpool_ch.bodenbedeckung_objektname oname, av_avdpool_ch.bodenbedeckung_boflaeche boflaeche
  WHERE pos.objektnamepos_von::text = oname.tid::text AND oname.objektname_von::text = boflaeche.tid::text AND boflaeche.art_txt::text = 'Gewaesser.fliessendes'::text;

ALTER TABLE av_basisplan.bodenbedeckung_objektname_v OWNER TO bpadmin;
GRANT ALL ON TABLE av_basisplan.bodenbedeckung_objektname_v TO bpadmin;
GRANT SELECT ON TABLE av_basisplan.bodenbedeckung_objektname_v TO mspublic;


-- DROP VIEW av_basisplan.bodenbedeckung_objektname_generalisiert_v;

CREATE OR REPLACE VIEW av_basisplan.bodenbedeckung_objektname_generalisiert_v AS 
 SELECT bodenbedeckung_objektname_v.ogc_fid, bodenbedeckung_objektname_v.tid, bodenbedeckung_objektname_v.objektnamepos_von, bodenbedeckung_objektname_v.pos, bodenbedeckung_objektname_v.ori, bodenbedeckung_objektname_v.rot, bodenbedeckung_objektname_v.hali_txt, bodenbedeckung_objektname_v.vali_txt, bodenbedeckung_objektname_v.groesse_txt, bodenbedeckung_objektname_v.gem_bfs, bodenbedeckung_objektname_v.los, bodenbedeckung_objektname_v.lieferdatum, bodenbedeckung_objektname_v.name, bodenbedeckung_objektname_v.art_txt, bodenbedeckung_objektname_v.xlabel, bodenbedeckung_objektname_v.ylabel, bodenbedeckung_objektname_v.area
   FROM av_basisplan.bodenbedeckung_objektname_v
  WHERE (bodenbedeckung_objektname_v.ogc_fid IN ( SELECT DISTINCT ON (st_x(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision)), st_y(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision))) bodenbedeckung_objektname_v.ogc_fid
           FROM av_basisplan.bodenbedeckung_objektname_v
          ORDER BY st_x(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision)), st_y(st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision)), st_distance(bodenbedeckung_objektname_v.pos, st_snaptogrid(bodenbedeckung_objektname_v.pos, 500::double precision))));

ALTER TABLE av_basisplan.bodenbedeckung_objektname_generalisiert_v OWNER TO bpadmin;
GRANT ALL ON TABLE av_basisplan.bodenbedeckung_objektname_generalisiert_v TO bpadmin;
GRANT SELECT ON TABLE av_basisplan.bodenbedeckung_objektname_generalisiert_v TO mspublic;


-- DROP VIEW av_basisplan.nomenklatur_gelaendename_v;

CREATE OR REPLACE VIEW av_basisplan.nomenklatur_gelaendename_v AS 
 SELECT pos.ogc_fid, pos.tid, pos.gelaendenamepos_von, pos.pos, 
        CASE
            WHEN pos.ori IS NULL THEN 100::double precision
            ELSE pos.ori
        END AS ori, pos.hali_txt, pos.vali_txt, pos.groesse_txt, pos.stil_txt, pos.gem_bfs, pos.los, pos.lieferdatum, gname.name, st_x(pos.pos) AS xlabel, st_y(pos.pos) AS ylabel
   FROM av_avdpool_ch.nomenklatur_gelaendenamepos pos, av_avdpool_ch.nomenklatur_gelaendename gname
  WHERE gname.tid::text = pos.gelaendenamepos_von::text;

ALTER TABLE av_basisplan.nomenklatur_gelaendename_v OWNER TO bpadmin;
GRANT ALL ON TABLE av_basisplan.nomenklatur_gelaendename_v TO bpadmin;
GRANT SELECT ON TABLE av_basisplan.nomenklatur_gelaendename_v TO mspublic;


-- DROP VIEW av_basisplan.nomenklatur_ortsname_v;

CREATE OR REPLACE VIEW av_basisplan.nomenklatur_ortsname_v AS 
 SELECT pos.ogc_fid, pos.tid, pos.ortsnamepos_von, pos.pos, 
        CASE
            WHEN pos.ori IS NULL THEN 100::double precision
            ELSE pos.ori
        END AS ori, pos.hali_txt, pos.vali_txt, pos.groesse_txt, pos.stil_txt, pos.gem_bfs, pos.los, pos.lieferdatum, oname.name, st_x(pos.pos) AS xlabel, st_y(pos.pos) AS ylabel
   FROM av_avdpool_ch.nomenklatur_ortsnamepos pos, av_avdpool_ch.nomenklatur_ortsname oname
  WHERE oname.tid::text = pos.ortsnamepos_von::text;

ALTER TABLE av_basisplan.nomenklatur_ortsname_v OWNER TO bpadmin;
GRANT ALL ON TABLE av_basisplan.nomenklatur_ortsname_v TO bpadmin;
GRANT SELECT ON TABLE av_basisplan.nomenklatur_ortsname_v TO mspublic;





