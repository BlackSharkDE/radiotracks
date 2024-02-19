/**
 * Die Notification-Funktionalität
 */

//Das Notification-Element
const notification = document.getElementById("notification");
notification.onclick = () => { hideNotification(); };

var notificationHideInterval = null; //Speichert den Interval für das Ausblenden der Notification (Animation selbst)
var notificationHideTimeout  = null; //Speichert den Timeout für das geplante Ausblenden der Notification

/**
 * Zeigt eine Notification an. (void - Funktion)
 * @param String HTML, welches innerhalb der Notification angezeigt werden soll
 * @param int    Nach wie vielen Sekunden die Notifiation automatisch ausgeblendet werden soll, 0 wenn gar nicht (OPTIONAL)
 * @param bool   Ob die Notification als wichtig (rot) markiert werden soll (OPTIONAL)
 */
function showNotification(notificationMessage,disappearAfter = 6,important = false) {

    let notificationIcon = '<i class="fa fa-info-circle"></i>'; //Icon innerhalb der Nachricht
    notification.style.color = "#ffffff"; //Standardmäßig weiße Schrift

    //Ob die Notification deutlicher markiert werden soll
    if(important) {
        notificationIcon = '<i class="fa fa-warning"></i>';
        notification.style.color = "#ff0000";
    }

    //Notification-Inhalt setzen
    notification.innerHTML = notificationIcon  + '&nbsp;' + notificationMessage;

    //Standardwerte setzen
    notification.style.opacity    = 0;
    notification.style.marginTop  = "-10px";
    notification.style.visibility = "visible";

    //Animation zum Anzeigen der Notification
    var showInterval = setInterval(() => {
        let opacity = parseFloat(notification.style.opacity);
        if(opacity < 1) {
            notification.style.opacity = opacity + 0.05;
        }

        let marginTop = parseFloat(notification.style.marginTop);
        if(marginTop < 30) {
            notification.style.marginTop = (marginTop + 2) + "px";
        }

        if(opacity == 1 && marginTop == 30) {
            clearInterval(showInterval);
        }
    },30);


    //Ob die Notification automatisch nach einer bestimmten Zeit ausgeblendet werden soll
    if(disappearAfter > 0) {
        if(!notificationHideTimeout) {
            notificationHideTimeout = setTimeout(hideNotification,disappearAfter * 1000);
        }
    } else {
        //Verhindere/überschreibe geplantes Ausblenden, sollte die Funktion erneut mit Parameterwert 0 aufgerufen worden sein
        clearInterval(notificationHideTimeout);
        notificationHideTimeout = null;
    }
}

/**
 * Blendet die Notification aus. (void - Funktion)
 */
function hideNotification() {

    //Verhindere mehrfaches Triggern des Effekts auf einmal
    if(!notificationHideInterval) {

        //Standardwerte setzen
        notification.style.opacity    = 1;
        notification.style.marginTop  = "30px";

        //Animation zum Ausblenden der Notification
        notificationHideInterval = setInterval(() => {
            let opacity = parseFloat(notification.style.opacity);
            if(opacity > 0) {
                notification.style.opacity = opacity - 0.05;
            }

            let marginTop = parseFloat(notification.style.marginTop);
            if(marginTop > -10) {
                notification.style.marginTop = (marginTop - 2) + "px";
            }

            if(opacity == 0 && marginTop == -10) {
                notification.style.visibility = "hidden";
                clearInterval(notificationHideInterval);
                notificationHideInterval = null;
                notificationHideTimeout  = null;
            }
        },30);
    }
}