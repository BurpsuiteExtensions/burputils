"""
    Burp utility module for Python Burp extensions. Author: Parsia Hakimian
    License: MIT

    # Usage
    1. Add it as a Python Burp module and use `from burputils import BurpUtils`.
        For more info see:
        https://parsiya.net/blog/2018-12-19-python-utility-modules-for-burp-extensions/
    2. Copy the files to the same path as your extension and use `from burputils
        import BurpUtils`.
        * These extra files do not have to be loaded in Burp, they just needs to
          be in the same path.
    3. Copy/paste used code into your extension.

    Please see README for details.
"""


class BurpUtils:
    """Helpers for Burp Python extensions"""

    def __init__(self, callbackHelper):
        """Set IExtensionHelpers
        
        Set with callbacks.getHelpers() in registerExtenderCallbacks.
        """
        self.burpHelper = callbackHelper
    
    def getInfoFromBytes(self, isRequest, rawBytes):
        """Process request or response from raw bytes.
        Returns IRequestInfo or IResponseInfo respectively.

        Use getInfo instead if you have access to an IHttpRequestResponse
        object. It allows you to use all methods like IRequestInfo.getUrl()
        later.

        Args:

        * isRequest (bool): Set to true if rawBytes is a request. false if it's a
            response.
        * rawBytes (byte[]): Raw bytes containing the request or response.
        """
        if isRequest:
            return self.burpHelper.analyzeRequest(rawBytes)
        else:
            return self.burpHelper.analyzeResponse(rawBytes)
    
    def getInfo(self, isRequest, requestResponse):
        """Process request or response from IHttpRequestResponse.
        Returns IRequestInfo or IResponseInfo respectively.

        This method is preferable to getInfoFromBytes.

        Args:

        * isRequest (bool): Set to true if rawBytes is a request. false if it's
            a response.
        * requestResponse (IHttpRequestResponse): Object containing the request
            or the response.
        """
        if isRequest:
            return self.burpHelper.analyzeRequest(requestResponse)
        else:
            return self.burpHelper.analyzeResponse(requestResponse.getResponse())
    
    def getBodyFromBytes(self, isRequest, rawBytes):
        """Extracts the body bytes from a request or response raw bytes.
        Returns a byte[] containing the body of the request or response.
        
        Args:

        * isRequest (bool): Set to true if rawBytes is a request. false if it's a
            response.
        * rawBytes (byte[]): Raw bytes containing the request or response.
        """
        info = self.getInfoFromBytes(isRequest, rawBytes)
        return rawBytes[info.getBodyOffset()]
    
    def getBody(self, isRequest, requestResponse):
        """Extracts the body bytes of an IHttpRequestResponse object.
        Returns a byte[] containing the body of the request or response.
        
        Args:

        * isRequest (bool): Set to true if rawBytes is a request. false if it's a
            response.
        * requestResponse (IHttpRequestResponse): Object containing the request
            or the response.
        """
        info = self.getInfo(isRequest, requestResponse)

        if isRequest:
            return requestResponse.getRequest()[info.getBodyOffset():]
        else:
            return requestResponse.getResponse()[info.getBodyOffset():]

    def getHeaders(self, info):
        """Extract the headers from an IRequestInfo or IResponseInfo object.
        Returns a Headers object with the headers.

        Args:

        * info (IRequestInfo or IResponseInfo): Request info. Use the output
            from getInfo or getInfoFromBytes.
        """
        from headers import Headers
        hdr = Headers()
        # this is IRequestInfo.getHeaders() or IResponseInfo.getHeaders() from Burp
        rawHdr = info.getHeaders()
        hdr.importRaw(rawHdr)
        return hdr
    
    def setRequestResponse(self, isRequest, message, requestResponse):
        """Set the request or response for an IHttpRequestResponse object.
        Does not return anything but requestResponse is modified.

        Args:

        * isRequest (bool): True if message is a request. False for response.
        * message (byte[]): Raw bytes of the request or response. Usually comes
            from buildHttpMessage.
        * requestResponse (IHttpRequestResponse): RequestResponse to be
            modified.
        """
        # if isRequest is True, use setRequest. Otherwise, setResponse.
        if isRequest:
            requestResponse.setRequest(message)
        else:
            requestResponse.setResponse(message)
    
    def runExternal(self, command, args):
        """Runs command with args via the command line.
        For the sake of simplicity, everything after the first item will be in a
        list of strings.

        Executes "command args[0] args[1] ...".

        Security implication: This is code-execution-as-a-service.

        Args:

        * command (string): Name of the command.
        * args (list of strings): Arguments in a Python list.
        """
        # alternatively, we could accept a string containing all the commands,
        # then run shlex.split and pass the result to popen.

        from subprocess import Popen, PIPE
        import sys

        # insert the command at the start of the list, everything gets shifted.
        args.insert(command, 0)
        # run everything
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        output = proc.stdout.read()
        proc.stdout.close()
        err = proc.stderr.read()
        proc.stderr.close()
        sys.stdout.write(err)
        return output
    
    def createHTTPMessage(self, headers, bodyBytes):
        """Create an HTTP message using IExtensionHelpers.buildHttpMessage with
        the headers in a Header object instead of a raw list.
        Returns a byte[] containing the HTTP message.

        Args:

        * headers (Header): Request headers in a Header object.
        * bodyBytes (byte[]): Raw bytes containing the body of the request.
        """
        return self.burpHelper.buildHttpMessage(headers.exportRaw(), bodyBytes)

    # IExtensionHelpers wrappers
    def base64Decode(self, base64Data):
        """Wrapper for IExtensionHelpers.base64Decode.
        Returns the decoded data.

        Args:

        * base64Data (byte[] or string): Base64 encoded data.
        """
        return self.burpHelper.base64Decode(base64Data)
    
    def base64Encode(self, data):
        """Wrapper for IExtensionHelpers.base64Encode.
        Returns the base64 encoding of input.

        Args:

        * data (byte[] or string): Data to be encoded.
        """
        return self.burpHelper.base64Encode(data)
