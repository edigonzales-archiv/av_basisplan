import geoscript.layer.Shapefile
import geoscript.filter.Filter
import geoscript.geom.Bounds
import geoscript.geom.Geometry

def kanton = new Shapefile("../data/kantonsgrenzen/kantonsgrenzen.shp")
def blatteinteilung_pk25 = new Shapefile("../data/blatteinteilung_pk25/blatteinteilung_pk25.shp")



Filter f1 = new Filter( "KANTONSNUM = 11" )
//kanton.eachFeature( f1 ) 
kanton.eachFeature()
{ 
    
    def list10000 = []
    def list5000 = []    
    
    ktnr = it.KANTONSNUM
    
    g1 = it.geom
    p1 = g1.bounds.getPolygon().getWkt()
    
    // Man muss wissen, wie die Geometriespalte heisst.
    // Bei Shapefiles "the_geom".
    Filter f2 = new Filter ( "INTERSECTS(the_geom, "+p1+")" )
    blatteinteilung_pk25.eachFeature ( f2 ) 
    {
        nr = it.nummer
        g2 = it.geom
        if ( g2.intersects( g1 ) )
        {
            b2 = g2.bounds
            
            println "Bounding Box Kachel: " + b2
            
            // 1:10000
            def list = quarter( b2, nr, "-", g1 )          
            list10000.addAll( list ) 
            
            // 1:5000
            list.each() 
            {
                b3 = new Bounds(it.xmin, it.ymin, it.xmax, it.ymax) 
                list = quarter( b3, it.nummer, "", g1 )
                list5000.addAll( list ) 
            }
            

            
        }
        
    }
        
    new File("bpav10000_"+ktnr+".csv").withWriter { out ->
        
        out.append "ID,XMIN,XMAX,YMIN,YMAX,nummer,kt_so"
        out.append '\n'
    
        list10000.each {
          def row = [it.id, it.xmin, it.xmax, it.ymin, it.ymax, it.nummer, it.ktso]
        out.append row.join(',')
        out.append '\n'
        }  
    }
    
    new File("bpav5000_"+ktnr+".csv").withWriter { out ->
        
        out.append "ID,XMIN,XMAX,YMIN,YMAX,nummer,kt_so"
        out.append '\n'        
        
        list5000.each {
          def row = [it.id, it.xmin, it.xmax, it.ymin, it.ymax, it.nummer, it.ktso]
        out.append row.join(',')
        out.append '\n'
        }  
    } 
        
}


def quarter( b1, nr, prefix, geom ) 
{
    def list = []
    
    // Kachel 1
    xmin = b1.getMinX()
    xmax = b1.getMinX() + ( b1.getMaxX() - b1.getMinX() ) / 2
    ymin = b1.getMinY() + ( b1.getMaxY() - b1.getMinY() ) / 2
    ymax = b1.getMaxY()
    
    Bounds b2 = new Bounds(xmin, ymin, xmax, ymax) 
    Geometry g2 = b2.getPolygon()
    
    //println (nr + ",  " + xmin +", "+ xmax + ", "+ ymin +", "+ ymax +", "+ nr + "-1,1" )    
    
    
    if ( geom.intersects( g2 ) ) 
    {
        def map = [:]
        map.put( "id", nr )
        map.put( "xmin", xmin )
        map.put( "xmax", xmax )
        map.put( "ymin", ymin )                
        map.put( "ymax", ymax )
        map.put( "nummer", nr+prefix+"1" )                
        map.put( "ktso", "1" ) 
        
        list.add( map )
    }
    
    // Kachel 2
    xmin = b1.getMinX() + ( b1.getMaxX() - b1.getMinX() ) / 2
    xmax = b1.getMaxX()
    ymin = b1.getMinY() + ( b1.getMaxY() - b1.getMinY() ) / 2
    ymax = b1.getMaxY()
    
    b2 = new Bounds(xmin, ymin, xmax, ymax) 
    g2 = b2.getPolygon()
   
    //println (nr + ",  " + xmin +", "+ xmax + ", "+ ymin +", "+ ymax +", "+ nr + "-2,1" )    
    
    if ( geom.intersects( g2 ) ) 
    {
        map = [:] 
        map.put( "id", nr )
        map.put( "xmin", xmin )
        map.put( "xmax", xmax )
        map.put( "ymin", ymin )                
        map.put( "ymax", ymax )
        map.put( "nummer", nr+prefix+"2" )                
        map.put( "ktso", "1" ) 
        
        list.add( map )
    }    
    // Kachel 3
    xmin = b1.getMinX()
    xmax = b1.getMinX() + ( b1.getMaxX() - b1.getMinX() ) / 2
    ymin = b1.getMinY()
    ymax = b1.getMinY() + ( b1.getMaxY() - b1.getMinY() ) / 2
    
    b2 = new Bounds(xmin, ymin, xmax, ymax) 
    g2 = b2.getPolygon()
   
    //println (nr + ",  " + xmin +", "+ xmax + ", "+ ymin +", "+ ymax +", "+ nr + "-3,1" )    

    if ( geom.intersects( g2 ) ) 
    {
        map = [:]
        map.put( "id", nr )
        map.put( "xmin", xmin )
        map.put( "xmax", xmax )
        map.put( "ymin", ymin )                
        map.put( "ymax", ymax )
        map.put( "nummer", nr+prefix+"3" )                
        map.put( "ktso", "1" ) 
        
        list.add( map )
    }
        
    // Kachel 4
    xmin = b1.getMinX() + ( b1.getMaxX() - b1.getMinX() ) / 2
    xmax = b1.getMaxX()
    ymin = b1.getMinY()
    ymax = b1.getMinY() + ( b1.getMaxY() - b1.getMinY() ) / 2
    
    b2 = new Bounds(xmin, ymin, xmax, ymax) 
    g2 = b2.getPolygon()
       
    //println (nr + ",  " + xmin +", "+ xmax + ", "+ ymin +", "+ ymax +", "+ nr + "-4,1" )    
    
    if ( geom.intersects( g2 ) ) 
    {
        map = [:]
        map.put( "id", nr )
        map.put( "xmin", xmin )
        map.put( "xmax", xmax )
        map.put( "ymin", ymin )                
        map.put( "ymax", ymax )
        map.put( "nummer", nr+prefix+"4" )                
        map.put( "ktso", "1" ) 
        
        list.add( map )
    }
    return list
}

