-- View: av_basisplan.einzelobjekte_punktelement_v

-- DROP VIEW av_basisplan.einzelobjekte_punktelement_v;

CREATE OR REPLACE VIEW av_basisplan.einzelobjekte_punktelement_v AS 
 SELECT pe.ogc_fid, pe.tid, pe.punktelement_von, pe.geometrie, pe.ori, pe.gem_bfs, pe.los, pe.lieferdatum, eo.art, eo.art_txt
   FROM av_avdpool_ch.einzelobjekte_einzelobjekt eo, av_avdpool_ch.einzelobjekte_punktelement pe
  WHERE pe.punktelement_von::text = eo.tid::text;

ALTER TABLE av_basisplan.einzelobjekte_punktelement_v OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.einzelobjekte_punktelement_v TO stefan;
GRANT SELECT ON TABLE av_basisplan.einzelobjekte_punktelement_v TO mspublic;

