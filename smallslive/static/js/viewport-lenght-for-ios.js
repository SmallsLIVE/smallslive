function viewPortLength(viewPort) {
    var browserName = navigator.userAgent.toLowerCase(); 
    if (browserName.indexOf('safari') != -1) { 
        if (browserName.indexOf('chrome') > -1) {
            if( viewPort === "height" )
                return window.innerHeight
            else if( viewPort === "width" )
                return window.innerWidth
        } else {  
            switch (window.orientation) {  
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
        }
    }
}