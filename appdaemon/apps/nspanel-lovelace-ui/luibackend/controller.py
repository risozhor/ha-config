import datetime
from helper import scale, pos_to_color, rgb_dec565

from pages import LuiPagesGen

class LuiController(object):

    def __init__(self, ha_api, config, send_mqtt_msg):
        self._ha_api = ha_api
        self._config = config
        self._send_mqtt_msg = send_mqtt_msg

        self._current_card = self._config._config_screensaver
        self._previous_cards = []
        # first card (default, after startup)
        self._previous_cards.append(self._config.getCard(0))
        
        self._pages_gen = LuiPagesGen(ha_api, config, send_mqtt_msg)

        # send panel back to startup page on restart of this script
        self._pages_gen.page_type("pageStartup")
        
        # time update callback
        time = datetime.time(0, 0, 0)
        ha_api.run_minutely(self._pages_gen.update_time, time)

        # Setup date callback
        ha_api.run_daily(self._pages_gen.update_date, time)

        # register callbacks
        self.register_callbacks()

        # calculate current brightness
        self.current_screensaver_brightness = self.calc_current_brightness(self._config.get("sleepBrightness"))
        self.current_screen_brightness      = self.calc_current_brightness(self._config.get("screenBrightness"))

        # register callbacks for each time
        if type(self._config.get("sleepBrightness")) == list:
            for index, timeset in enumerate(self._config.get("sleepBrightness")):
                self._ha_api.run_daily(self.update_screensaver_brightness, timeset["time"], ssbr=timeset["value"], sbr=self.current_screen_brightness)
        

        # call update_screensaver_brightness on changes of entity configured in sleepTracking
        bst = self._config.get("sleepTracking")
        if bst is not None and self._ha_api.entity_exists(bst):
            self._ha_api.listen_state(self.update_screensaver_brightness_state_callback, entity_id=bst)
        
        # call update_screensaver_brightness on entity configured in sleepOverride
        sleepOverride = self._config.get("sleepOverride")
        if sleepOverride is not None and type(sleepOverride) is dict  and sleepOverride["entity"] is not None and sleepOverride["brightness"] is not None and self._ha_api.entity_exists(sleepOverride["entity"]):
            self._ha_api.log(f"Configuring Sleep Override. Config is {sleepOverride}")
            self._ha_api.listen_state(self.update_screensaver_brightness_state_callback, entity_id=sleepOverride["entity"])

        # register callback for state changes on tracked value (for input_number) - sleepBrightness
        sleep_brightness_config = self._config.get("sleepBrightness")
        if type(sleep_brightness_config) == str and self._ha_api.entity_exists(sleep_brightness_config):
            self._ha_api.listen_state(self.update_screensaver_brightness_state_callback, entity_id=sleep_brightness_config)
        # register callback for state changes on tracked value (for input_number) - screenBrightness
        screen_brightness_config = self._config.get("screenBrightness")
        if type(screen_brightness_config) == str and self._ha_api.entity_exists(screen_brightness_config):
            self._ha_api.listen_state(self.update_screensaver_brightness_state_callback, entity_id=screen_brightness_config)            

    def startup(self):
        self._ha_api.log(f"Startup Event")
        # send time and date on startup
        self._pages_gen.update_time("")
        self._pages_gen.update_date("")

        # set screensaver timeout
        timeout = self._config.get("sleepTimeout")
        self._send_mqtt_msg(f"timeout~{timeout}")
        
        # set current screensaver brightness
        self.update_screensaver_brightness(kwargs={"ssbr": self.current_screensaver_brightness, "sbr": self.current_screen_brightness})
        
        # send panel to screensaver
        self._pages_gen.render_card(self._current_card)


    def update_screensaver_brightness_state_callback(self, entity, attribute, old, new, kwargs):
        if type(self._config.get("sleepBrightness")) == str:
            self.current_screensaver_brightness = self.calc_current_brightness(self._config.get("sleepBrightness"))
            self.current_screen_brightness      = self.calc_current_brightness(self._config.get("screenBrightness"))
        self.update_screensaver_brightness(kwargs={"ssbr": self.current_screensaver_brightness, "sbr": self.current_screen_brightness})
        
    def update_screensaver_brightness(self, kwargs):
        bst = self._config.get("sleepTracking")
        sleepOverride = self._config.get("sleepOverride")
        sOEntity = None
        sOBrightness = None
        if sleepOverride is not None and type(sleepOverride) is dict:
            sOEntity = sleepOverride["entity"]
            sOBrightness = sleepOverride["brightness"]

        sleepBrightness = 0
        brightness = self.calc_current_brightness(self._config.get("screenBrightness"))

        if bst is not None and self._ha_api.entity_exists(bst) and self._ha_api.get_entity(bst).state in self._config.get("sleepTrackingZones"):
            self._ha_api.log(f"sleepTracking setting brightness to 0")
            sleepBrightness = 0

        elif sOEntity is not None and sOBrightness is not None and self._ha_api.entity_exists(sOEntity) and self._ha_api.get_entity(sOEntity).state in ["on", "true", "home"]:
            self._ha_api.log(f"sleepOverride setting brightness to {sOBrightness}")
            sleepBrightness = sOBrightness
        
        else:
            self.current_screensaver_brightness = kwargs['ssbr']
            sleepBrightness                     = self.current_screensaver_brightness
            self.current_screen_brightness      = kwargs['sbr']
            brightness                          = self.current_screen_brightness
        # same value for both values will break sleep timer of the firmware
        if sleepBrightness==brightness:
            sleepBrightness = sleepBrightness-1

        # background color
        dbc = 0
        defaultBackgroundColor = self._config.get("defaultBackgroundColor")
        if type(defaultBackgroundColor) is str:
            if defaultBackgroundColor == "ha-dark":
                dbc = 6371
            elif defaultBackgroundColor == "black":
                dbc = 0
        elif type(defaultBackgroundColor) is list:
            dbc = rgb_dec565(defaultBackgroundColor)

        self._send_mqtt_msg(f"dimmode~{sleepBrightness}~{brightness}~{dbc}")
        
    def calc_current_brightness(self, sleep_brightness_config):
        current_screensaver_brightness = 20
        #sleep_brightness_config = self._config.get("sleepBrightness")
        # set brightness of screensaver
        if type(sleep_brightness_config) == int:
            current_screensaver_brightness = sleep_brightness_config
        elif type(sleep_brightness_config) == str:
                current_screensaver_brightness = int(float(self._ha_api.get_state(sleep_brightness_config)))
        elif type(sleep_brightness_config) == list:
            sorted_timesets = sorted(sleep_brightness_config, key=lambda d: self._ha_api.parse_time(d['time']))
            # calc current screensaver brightness
            found_current_dim_value = False
            for i in range(len(sorted_timesets)):
                found = self._ha_api.now_is_between(sorted_timesets[i-1]['time'], sorted_timesets[i]['time'])
                if found:
                    found_current_dim_value = True
                    current_screensaver_brightness = sorted_timesets[i-1]['value']
            # still no dim value
            if not found_current_dim_value:
                self._ha_api.log("Chooseing %s as fallback", sorted_timesets[0])
                current_screensaver_brightness = sorted_timesets[0]["value"]
        return current_screensaver_brightness
    
    def register_callbacks(self):
        items = self._config.get_all_entity_names()
        self._ha_api.log(f"Registering callbacks for the following items: {items}")
        for item in items:
            if self._ha_api.entity_exists(item):
                self._ha_api.listen_state(self.state_change_callback, entity_id=item, attribute="all")

    def state_change_callback(self, entity, attribute, old, new, kwargs):
        self._ha_api.log(f"Got callback for: {entity}", level="DEBUG")
        self._ha_api.log(f"Current page has the following items: {self._current_card.get_entity_names()}", level="DEBUG")
        if entity in self._current_card.get_entity_names():
            self._ha_api.log(f"Callback Entity is on current page: {entity}", level="DEBUG")
            self._pages_gen.render_card(self._current_card, send_page_type=False)
            # send detail page update, just in case
            if self._current_card.cardType in ["cardGrid", "cardEntities"]:
                if entity.startswith("light"):
                    self._pages_gen.generate_light_detail_page(entity)
                if entity.startswith("cover"):
                    self._pages_gen.generate_shutter_detail_page(entity)
                if entity.startswith("fan"):
                    self._pages_gen.generate_fan_detail_page(entity)


    def detail_open(self, detail_type, entity_id):
        if detail_type == "popupShutter":
            self._pages_gen.generate_shutter_detail_page(entity_id)
        if detail_type == "popupLight":
            self._pages_gen.generate_light_detail_page(entity_id)
        if detail_type == "popupFan":
            self._pages_gen.generate_fan_detail_page(entity_id)

    def button_press(self, entity_id, button_type, value):
        self._ha_api.log(f"Button Press Event; entity_id: {entity_id}; button_type: {button_type}; value: {value} ")
        # internal buttons
        if entity_id == "screensaver" and button_type == "bExit":
            # get default card if there is one
            defaultCard = self._config.get("screensaver.defaultCard")
            if defaultCard is not None:
                defaultCard = self._ha_api.render_template(defaultCard)
                self._ha_api.log(f"Searching for the following page as defaultPage: {defaultCard}")
                dstCard = self._config.searchCard(defaultCard)
                self._ha_api.log(f"Result for the following page as defaultPage: {dstCard}")
                if dstCard is not None:
                    self._previous_cards = []
                    self._previous_cards.append(dstCard)
            # set _previous_cards to first page in case it's empty
            if len(self._previous_cards) == 0:
                self._previous_cards.append(self._config.getCard(0))
            # check for double tap if configured and render current page
            if self._config.get("screensaver.doubleTapToUnlock") and int(value) >= 2:
                self._current_card = self._previous_cards.pop()
                self._pages_gen.render_card(self._current_card)
            elif not self._config.get("screensaver.doubleTapToUnlock"):
                self._current_card = self._previous_cards.pop()
                self._pages_gen.render_card(self._current_card)
            return
            
        if button_type == "sleepReached":
            self._previous_cards.append(self._current_card)
            self._current_card = self._config._config_screensaver
            self._pages_gen.render_card(self._current_card)
            return

        if button_type == "bExit":
            self._pages_gen.render_card(self._current_card)
        if button_type == "bUp":
            self._current_card = self._previous_cards.pop()
            self._pages_gen.render_card(self._current_card)

        if button_type == "bNext":
            card = self._config.getCard(self._current_card.pos+1)
            self._current_card = card
            self._pages_gen.render_card(card)
        if button_type == "bPrev":
            card = self._config.getCard(self._current_card.pos-1)
            self._current_card = card
            self._pages_gen.render_card(card)
        
        elif entity_id == "updateDisplayNoYes" and value == "no":
            self._pages_gen.render_card(self._current_card)

        # buttons with actions on HA
        if button_type == "OnOff":
            if value == "1":
                self._ha_api.turn_on(entity_id)
            else:
                self._ha_api.turn_off(entity_id)

        if button_type == "number-set":
            if entity_id.startswith('fan'):
                entity = self._ha_api.get_entity(entity_id)
                value = float(value)*float(entity.attributes.get("percentage_step", 0))
                entity.call_service("set_percentage", percentage=value)
            else:
                self._ha_api.get_entity(entity_id).call_service("set_value", value=value)

        # for shutter / covers
        if button_type == "up":
            self._ha_api.get_entity(entity_id).call_service("open_cover")
        if button_type == "stop":
            self._ha_api.get_entity(entity_id).call_service("stop_cover")
        if button_type == "down":
            self._ha_api.get_entity(entity_id).call_service("close_cover")
        if button_type == "positionSlider":
            pos = int(value)
            self._ha_api.get_entity(entity_id).call_service("set_cover_position", position=pos)
        if button_type == "tiltOpen":
            self._ha_api.get_entity(entity_id).call_service("open_cover_tilt")
        if button_type == "tiltStop":
            self._ha_api.get_entity(entity_id).call_service("stop_cover_tilt")
        if button_type == "tiltClose":
            self._ha_api.get_entity(entity_id).call_service("close_cover_tilt")
        if button_type == "tiltSlider":
            pos = int(value)
            self._ha_api.get_entity(entity_id).call_service("set_cover_tilt_position", position=pos)


        if button_type == "button":
            if entity_id.startswith('uuid'):
                le = self._config._config_entites_table.get(entity_id)
                entity_id = le.entityId

            if entity_id.startswith('navigate'):
                # internal for navigation to nested pages
                dstCard = self._config.searchCard(entity_id)
                if dstCard is not None:
                    self._previous_cards.append(self._current_card)
                    self._current_card = dstCard
                    self._pages_gen.render_card(self._current_card)
                else:
                    self._ha_api.log(f"No page with key {entity_id} found")
            elif entity_id.startswith('scene'):
                self._ha_api.get_entity(entity_id).call_service("turn_on")
            elif entity_id.startswith('script'):
                self._ha_api.get_entity(entity_id).call_service("turn_on")
            elif entity_id.startswith('light') or entity_id.startswith('switch') or entity_id.startswith('input_boolean') or entity_id.startswith('automation') or entity_id.startswith('fan'):
                self._ha_api.get_entity(entity_id).call_service("toggle")
            elif entity_id.startswith('lock'):
                if self._ha_api.get_entity(entity_id).state == "locked":
                    self._ha_api.get_entity(entity_id).call_service("unlock")
                else:
                    self._ha_api.get_entity(entity_id).call_service("lock")
            elif entity_id.startswith('button') or entity_id.startswith('input_button'):
                self._ha_api.get_entity(entity_id).call_service("press")
            elif entity_id.startswith('input_select'):
                self._ha_api.get_entity(entity_id).call_service("select_next")
            elif entity_id.startswith('vacuum'):
                if self._ha_api.get_entity(entity_id).state == "docked":
                    self._ha_api.get_entity(entity_id).call_service("start")
                else:
                    self._ha_api.get_entity(entity_id).call_service("return_to_base")

        # for media page
        if button_type == "media-next":
            self._ha_api.get_entity(entity_id).call_service("media_next_track")
        if button_type == "media-back":
            self._ha_api.get_entity(entity_id).call_service("media_previous_track")
        if button_type == "media-pause":
            self._ha_api.get_entity(entity_id).call_service("media_play_pause")
        if button_type == "media-OnOff":
            if self._ha_api.get_entity(entity_id).state == "off":
                self._ha_api.get_entity(entity_id).call_service("turn_on")
            else:
                self._ha_api.get_entity(entity_id).call_service("turn_off")
        if button_type == "volumeSlider":
            pos = int(value)
            # HA wants this value between 0 and 1 as float
            pos = pos/100
            self._ha_api.get_entity(entity_id).call_service("volume_set", volume_level=pos)
        if button_type == "speaker-sel":
            self._ha_api.get_entity(entity_id).call_service("select_source", source=value)
            
        # for light detail page
        if button_type == "brightnessSlider":
            # scale 0-100 to ha brightness range
            brightness = int(scale(int(value),(0,100),(0,255)))
            self._ha_api.get_entity(entity_id).call_service("turn_on", brightness=brightness)
        if button_type == "colorTempSlider":
            entity = self._ha_api.get_entity(entity_id)
            #scale 0-100 from slider to color range of lamp
            color_val = scale(int(value), (0, 100), (entity.attributes.min_mireds, entity.attributes.max_mireds))
            self._ha_api.get_entity(entity_id).call_service("turn_on", color_temp=color_val)
        if button_type == "colorWheel":
            self._ha_api.log(value)
            value = value.split('|')
            color = pos_to_color(int(value[0]), int(value[1]), int(value[2]))
            self._ha_api.log(color)
            self._ha_api.get_entity(entity_id).call_service("turn_on", rgb_color=color)
        
        # for climate page
        if button_type == "tempUpd":
            temp = int(value)/10
            self._ha_api.get_entity(entity_id).call_service("set_temperature", temperature=temp)
        if button_type == "tempUpdHighLow":
            value = value.split("|")
            temp_high = int(value[0])/10
            temp_low  = int(value[1])/10
            self._ha_api.get_entity(entity_id).call_service("set_temperature", target_temp_high=temp_high, target_temp_low=temp_low)
        if button_type == "hvac_action":
            self._ha_api.get_entity(entity_id).call_service("set_hvac_mode", hvac_mode=value)
            
        # for alarm page
        if button_type in ["disarm", "arm_home", "arm_away", "arm_night", "arm_vacation"]:
            self._ha_api.get_entity(entity_id).call_service(f"alarm_{button_type}", code=value)
        if button_type == "opnSensorNotify":
            msg = ""
            entity = self._ha_api.get_entity(entity_id)
            if "open_sensors" in entity.attributes and entity.attributes.open_sensors is not None:
                for e in entity.attributes.open_sensors:
                    msg += f"- {self._ha_api.get_entity(e).attributes.friendly_name}\r\n"
            self._pages_gen.send_message_page("opnSensorNotifyRes", "", msg, "", "")

