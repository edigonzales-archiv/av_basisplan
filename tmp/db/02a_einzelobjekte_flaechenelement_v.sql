-- View: av_basisplan.einzelobjekte_flaechenelement_v

-- DROP VIEW av_basisplan.einzelobjekte_flaechenelement_v;

CREATE OR REPLACE VIEW av_basisplan.einzelobjekte_flaechenelement_v AS 
 SELECT fe.ogc_fid, fe.tid, fe.flaechenelement_von, fe.geometrie, fe.gem_bfs, fe.los, fe.lieferdatum, eo.art, eo.art_txt
   FROM av_avdpool_ch.einzelobjekte_einzelobjekt eo, av_avdpool_ch.einzelobjekte_flaechenelement fe
  WHERE fe.flaechenelement_von::text = eo.tid::text;

ALTER TABLE av_basisplan.einzelobjekte_flaechenelement_v OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.einzelobjekte_flaechenelement_v TO stefan;
GRANT SELECT ON TABLE av_basisplan.einzelobjekte_flaechenelement_v TO mspublic;

