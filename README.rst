Anti-captcha approaches:
    scanner_task/bypassing/cursor_movement.py

        - Simulates mouse movements asynchronously on non-headless instances
        Result: able to bypass login captcha consistently, but not futher ones

    scanner_task/bypassing/cookie_utils.py - generate_cookie_noise()

        - Simulates user navigation  to other sites to bypass fingerprinting to some extent
        Result: Had no real impact on the tests

    scanner_task/navigation/setup.py

        - Instantiate the chrome webdriver with recommended anti-detection options
        - Use of selenium_stealth library to spoof User Agent and similiar attributes on the webdriver - https://github.com/diprajpatra/selenium-stealth
        - Use of custom webdriver managed by undetected-chromedriver - https://github.com/ultrafunkamsterdam/undetected-chromedriver
        Result: Browser passes all static page tests

    using free proxylists

        - traffic was too slow, the pages wouldn't even load
        - plus, public free proxies do not have the best reputation and are easily detected by captcha fingerprinting
        Result: Didn't work

    local proxy using proxy.py

        - https://github.com/abhinavsingh/proxy.py
        - Tried instantiating a local proxy to filter requests to some given domains (Especifically ../Ss13U803/init.js)
        - It sort of works, but only if the outcoming requests uses HTTP protocol, because the request params are not exposed
        in HTTPS, requiring to break the SSL/TLS from the outbound packages.
        - Upwork's server requests always redirect to HTTPS
        - Command:
            $ proxy --plugin proxy.plugin.FilterByURLRegexPlugin --filtered-client-urls -<config_file.json>
        Result: Didn't work

    Browser's network request block option

        - After some analysis(some drafts included on notes/), I noticed that the script that initiates the exchange of user data between
        the client and both the CDN and the captcha servers was -> 'https://www.upwork.com/Ss13U803/init.js'
        - Applying a simple filter like 'www.upwork.com/Ss13U803*' on chrome network options is enough for the captcha to never trigger again
        - Unfortunately, this resource isn't accessible to selenium nor webdriver Chrome options, requiring me to click it manually or to automate
        this process using some GUI automation tool
        Result: Worked flawlessly, but I couldn't automate it


The Evil entity - https://www.upwork.com/Ss13U803/init.js




