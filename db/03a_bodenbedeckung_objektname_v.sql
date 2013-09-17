-- View: av_basisplan.bodenbedeckung_objektname_v

-- DROP VIEW av_basisplan.bodenbedeckung_objektname_v;

CREATE OR REPLACE VIEW av_basisplan.bodenbedeckung_objektname_v AS 
 SELECT pos.ogc_fid, pos.tid, pos.objektnamepos_von, pos.pos, pos.ori, 
        CASE
            WHEN pos.ori IS NULL THEN 0::double precision
            ELSE (100::double precision - pos.ori) * 0.9::double precision
        END AS rot, pos.hali_txt, pos.vali_txt, pos.groesse_txt, pos.gem_bfs, pos.los, pos.lieferdatum, oname.name, boflaeche.art_txt, st_x(pos.pos) AS xlabel, st_y(pos.pos) AS ylabel, st_area(boflaeche.geometrie) AS area
   FROM av_avdpool_ch.bodenbedeckung_objektnamepos pos, av_avdpool_ch.bodenbedeckung_objektname oname, av_avdpool_ch.bodenbedeckung_boflaeche boflaeche
  WHERE pos.objektnamepos_von::text = oname.tid::text AND oname.objektname_von::text = boflaeche.tid::text AND boflaeche.art_txt::text = 'Gewaesser.fliessendes'::text;

ALTER TABLE av_basisplan.bodenbedeckung_objektname_v OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.bodenbedeckung_objektname_v TO stefan;
GRANT SELECT ON TABLE av_basisplan.bodenbedeckung_objektname_v TO mspublic;

