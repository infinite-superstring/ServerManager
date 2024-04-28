/**
 * plugins/index.js
 *
 * Automatically included in `./src/main.js`
 */

// Plugins
import vuetify from './vuetify'
import router from '../router'
import vuetifyInstance from '@/plugins/vuetify' //Or wherever you have your vuetify instance
import {Vuetify3Dialog} from 'vuetify3-dialog'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

export function registerPlugins (app) {
  app
    .use(vuetify)
    .use(router)
    .use(Vuetify3Dialog, {
      vuetify: vuetifyInstance, //You must pass your vuetify instance as an option
      defaults: {
        //You can pass default options for dialogs, dialog's card, snackbars or bottom-sheets here
      }
    })
    .use(pinia)
}
