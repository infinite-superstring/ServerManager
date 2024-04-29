<template>

  <v-container class="machine-list">
    <v-row no-gutters>
      <v-col
        v-for="n in 10"
        :key="n"
        cols="12"
        sm="4"
      >
        <v-sheet class="ma-2">
          <v-card>
            <v-card-title class="machine-name">
              实例名
              <div class="machine-action">
                <v-btn size="x-small">修改Token</v-btn>
                <v-btn size="x-small">删除节点</v-btn>
              </div>
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col
                  v-for="n in 7"
                  :key="n"
                  cols="16"
                  sm="3"
                >
                  <div class="status">
                    <div class="status-name">
                      CPU
                    </div>
                    <div class="status-value">
                      10%
                    </div>
                  </div>
                </v-col>

              </v-row>
              <v-row>
                <v-col
                  cols="12"
                  sm="6"
                >
                  占用率图
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                >
                  占用率图
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          <!--          <v-card>-->
          <!--            <v-img-->
          <!--              src="@/assets/images/Machine1.png"-->
          <!--              class="align-end"-->
          <!--              gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"-->
          <!--              height="200px"-->
          <!--              min-width="30vw"-->
          <!--              cover-->
          <!--            >-->
          <!--              <v-card-title class="text-white" v-text="text"></v-card-title>-->
          <!--            </v-img>-->

          <!--            <v-card-actions>-->
          <!--              <v-spacer></v-spacer>-->

          <!--              <v-btn size="small" color="surface-variant" variant="text" prepend-icon="mdi:mdi-play">控制</v-btn>-->

          <!--              <v-btn size="small" color="surface-variant" variant="text" prepend-icon="mdi:mdi-tune">设置</v-btn>-->

          <!--              <v-btn size="small" color="surface-variant" variant="text" icon="mdi-share-variant"></v-btn>-->
          <!--            </v-card-actions>-->
          <!--          </v-card>-->
          <!--          <v-card-->
          <!--            hover-->
          <!--            title="实例名"-->
          <!--            subtitle="实例备注"-->
          <!--          >-->
          <!--            <template v-slot:append>-->
          <!--              <v-icon color="success" icon="mdi-check"></v-icon>-->
          <!--            </template>-->

          <!--            <v-card-text>-->
          <!--              实例状态-->
          <!--            </v-card-text>-->
          <!--          </v-card>-->
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'MachineList',
  data() {
    return {
      text: "测试文本"
    }
  }
}
</script>

<style>
.machine-name {
  display: flex;
  justify-content: space-between;
}
.machine-list {
  max-width: 100%
}
</style>
