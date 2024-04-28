<template>
  <v-app>
    <LayoutsHeader />
    <v-main>
      <router-view />
    </v-main>
<!--    <LayoutsFooter />-->
  </v-app>
</template>

<script setup>
  //
import LayoutsFooter from "@/layouts/default/Footer.vue";
  import LayoutsHeader from "@/layouts/default/Header.vue";
</script>
