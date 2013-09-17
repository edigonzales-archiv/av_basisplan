-- View: av_basisplan.einzelobjekte_linienelement_v

-- DROP VIEW av_basisplan.einzelobjekte_linienelement_v;

CREATE OR REPLACE VIEW av_basisplan.einzelobjekte_linienelement_v AS 
 SELECT le.ogc_fid, le.tid, le.linienelement_von, le.geometrie, le.gem_bfs, le.los, le.lieferdatum, eo.art, eo.art_txt
   FROM av_avdpool_ch.einzelobjekte_einzelobjekt eo, av_avdpool_ch.einzelobjekte_linienelement le
  WHERE le.linienelement_von::text = eo.tid::text;

ALTER TABLE av_basisplan.einzelobjekte_linienelement_v OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.einzelobjekte_linienelement_v TO stefan;
GRANT SELECT ON TABLE av_basisplan.einzelobjekte_linienelement_v TO mspublic;

