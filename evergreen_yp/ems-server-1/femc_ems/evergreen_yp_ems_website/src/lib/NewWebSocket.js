export default function (onMessageCallBack, onErrorCallBack, EnvSocketURL, extData, token) {
    try {
      let VUE_APP_WebSucket_URL = EnvSocketURL ?? process.env.VUE_APP_WebSucket_URL;
      if (VUE_APP_WebSucket_URL.indexOf(":") == -1) {
        VUE_APP_WebSucket_URL = (window.location.origin + VUE_APP_WebSucket_URL).replace(/https/gi, "wss").replace(/http/gi, "ws");
      }
  
      var socket = new WebSocket(VUE_APP_WebSucket_URL);

      // 發送初始消息
      socket.onopen = function () {
        if (token) {
          const auth_message = {
            'action': 'auth',
            'token': token
          }
          socket.send(JSON.stringify(auth_message));
        }
      };

      socket.onmessage = function (raw) {
        try {
          if (onMessageCallBack) {
            onMessageCallBack(raw.data ?? raw);
          }
        } catch (error) {
          console.log("Error: " + error.message);
        }
      };
  
      socket.onerror = function (event) {
        if (onErrorCallBack) {
          //{URL , ESSName, socketObjet}
          onErrorCallBack(VUE_APP_WebSucket_URL, extData?.ESSName, extData?.socketObjet);
        }
        socket.close();
      };
  
      return socket;
    } catch {
      return null;
    }
  }
  
  