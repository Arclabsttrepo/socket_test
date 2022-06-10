#include "client.hpp"
#include <sl/Camera.hpp>

#define NODE_NAME "client5"
#define PORT 5050
#define SERVER "127.0.1.1"

float message_float = 0;
json stateTrajectory = json::array();
stateTrajectory = {};

float scandepth(int leftCol, int u, int width, int height, float depthBound,float *depths){
  float distanceCount = 0;

  for(int i = leftCol; i != u + leftCol; i++){
      //iterate through width space
      for (int q = 0; q != height-1; q++){
        //iterate through top right quadrant
        int pixVal = i + width*q;
        //std::cout <<"pixel sel: "<<pixval<<'\n';
        float depth = depths[pixVal];
        //float depth=1;
        if (depth < depthBound){
            distanceCount = distanceCount + 1;
            //std::cout <<"x: "<< q << " " << "y: " << i << " " <<"pixval: " << pixval << " " <<"distance: " << depth<< '\n';
        }
        
      }
       
    }

  float columnArea = u*height;
    float percCovered = distanceCount/columnArea;
    return percCovered;
}

void depthCallback()
{
  // Get a pointer to the depth values casting the data
  // pointer to floating point
  float* depths = (float*)(&msg->data[0]);     //replace with ZED SDK depth map/image

  // Image coordinates of the center pixel
  //int u = msg->width / 2;
  //int v = msg->height / 2;

  // Linear index of the center pixel
  //int centerIdx = u + msg->width * v;
  //int alpha=4; //width aspect must be greater than 2
  //int beta=3; //height aspect must be greater than 2
  

  int u = 388; //robot width at 1 meter perspective projection
  int v = 357; //robot height at 1 meter perspective projection
  int cammid = 1104; //zed camera middle
  float mmpx = 1.29;
//int leftwidtharr[6]={164,358,552,746,910,940};
  int leftWidthArray[6] = {910,716,522,328,134}; //
  int rightWidthArray[6] = {1104,1298,1492,1686,1880,2074}; 
  int widthCenter = 910;
  float depthBound = 0.75;
  float areaCoverThresh = 0.1;

    int height = (msg->height); //replace with ZED SDK height
    int width = (msg->width); //replace with ZED SDK width
   // float column_area=u*(msg->height);
   // float perc_covered=distance_count/column_area;
    float percCovered = scandepth(widthCenter, u, width, height, depthBound, depths);
   // std::string msg_string="";
    if (percCovered > areaCoverThresh){
      //Start scanning algorithm
      //Start left array first, then move to right 
      int acheived = 0;
      //Scan Left 55degree FOV
      for (int ll = 0; ll != 6; ll++){
          percCovered = scandepth(leftWidthArray[ll], u, width, height, depthBound, depths);
          if (percCovered < areaCoverThresh){
            acheived = 1 + acheived;
            float distcent = tan(0.001*mmpx*(cammid-(leftWidthArray[ll]+u)/2));
            //msg_string_string_stream << "L:" << distcent;
            message_float.data = distcent;
            std::cout <<"Left choice percCov:"<<percCovered<<" column:"<<ll<<" ang: "<<distcent<<'\n';
            break;
          }
          percCovered = scandepth(rightWidthArray[ll], u, width, height, depthBound, depths);
            if (percCovered < areaCoverThresh){
              acheived = 1 + acheived;
              std::cout <<"Right percCov:"<<percCovered<<" column:"<<ll<<'\n';
              float distcent = tan(0.001*mmpx*(-cammid+(rightWidthArray[ll]+u)/2));
              message_float.data = distcent;
              break;
            }

      }

      if(acheived==0){
            std::cout <<"Rotate:"<<'\n';
            float distcent = 3.14;
            message_float = distcent;

      }
      //Did not get any passable columns in left try right

    }else{
      std::cout <<"Center percCov:"<<percCovered<<'\n';
      message_float = 0;
    }

  }

void State_Machine(json state, int sock){
  float xk = state["msg"][0];
  float yk = state["msg"][1];
  float phik = state["msg"][2];

  float phidk = message_float + phik; //converting from python to c++??
  float xd = xk + cos(phidk);
  float yd = yk + sin(phidk);

  stateTrajectory = {xd,yd,phidk};
  Push(sock, "state_machine", "nav", stateTrajectory);
}


int main(){
  json variableList = json::array();
  variableList = {};
  json variableNameList = json::array();
  variableNameList = {"state"};

  json state;

  int sock = connectClient(PORT, SERVER);
  Send(sock, "watchdog", "blank", NODE_NAME);

  while(true){
    variableList = Msg_Handler(variableList, variableNameList,sock);

    state = variableList[0];       

  }   

return 0;
}