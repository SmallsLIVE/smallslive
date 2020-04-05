function viewPortLength(viewPort) {
    var browserName = navigator.userAgent.toLowerCase(); 
    if (browserName.indexOf('safari') != -1) { 
        windowOrientation = (window.orientation, 90)
        switch (windowOrientation) {  
            case 0:  
                if( viewPort === "height" )
                    return window.innerWidth
                else if( viewPort === "width" )
                    return window.innerHeight
                break;
                
            case 180:  
                if( viewPort === "height" )
                    return window.innerWidth
                else if( viewPort === "width" )
                    return window.innerHeight
                break;
            
            case -90:  
                if( viewPort === "height" )
                    return window.innerHeight
                else if( viewPort === "width" )
                    return window.innerWidth
                break;
            
            case 90:                  
                if( viewPort === "height" )
                    return window.innerHeight
                else if( viewPort === "width" )
                    return window.innerWidth
                break; 
        }
    }else{
        if( viewPort === "height" )
            return window.innerHeight
        else if( viewPort === "width" )
            return window.innerWidth
    }
}