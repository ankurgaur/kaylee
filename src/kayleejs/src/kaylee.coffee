kl = {
    node:  { # node state
        id : null
    }
    classes  : {}
    config:
        root : '/kaylee'
}


class Event
    constructor : () ->
        @callbacks = []

    trigger : (args...) ->
        for c in @callbacks
            c(args...)

    bind : (callback) ->
        @callbacks.push(callback)

    unbind : (callback) ->
        @callbacks[t..t] = [] if (t = @callbacks.indexOf(callback)) > -1

kl.classes.Event = Event


# kl.ajax is currently using jQuery.ajax()
kl.ajax = (url, reqtype, data, success, error) ->
   $.ajax(
        url: url,
        type: reqtype
        data: data,
        dataType: 'json'
        success: (data) ->
            success(data) if success?
            #sf.status.unlock() if not data.error?
        error: (jqXHR, status_text) ->
            if error? then error(status_text) else kl.error(status_text)
            # sf.status.error("""Connection #{status_text}.
            # Please Refresh the page and try again.""", false)
    )
    return null

kl.post = (url, data, success, error) ->
    _success = (data) ->
        if data.error? then error(data.error) else success(data)
    kl.ajax(url, 'POST', data, _success, error)
    return null

kl.get = (url, success, error) ->
    _success = (data) ->
        if data.error? then error(data.error) else success(data)
    kl.ajax(url, 'GET', {}, success, error)
    return null

kl.error = (err) ->
    alert('Kaylee has encountered an unexpected error: #{err}')

kl.start = (callback) ->
    kl.get("#{kl.config.root}/register",
        (data) ->
            kl.node.id = data.nid
            callback(data) if callback?
            kl.node_registered.trigger(data)
    )

kl.subscribe = (app_name, callback) ->
    kl.get("#{kl.config.root}/apps/#{app_name}/subscribe/#{kl.node.id}",
        (data) ->
            callback(data) if callback?
            kl.node_subscribed.trigger(data)
    )

# Kaylee events
kl.node_registered = new Event()
kl.node_subscribed = new Event()

window.kl = kl;