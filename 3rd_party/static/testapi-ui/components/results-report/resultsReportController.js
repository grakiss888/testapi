/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
    'use strict';

    angular
        .module('testapiApp')
        .controller('ResultsReportController', ResultsReportController);

    ResultsReportController.$inject = [
        '$http', '$stateParams', '$window',
        '$uibModal', 'testapiApiUrl', 'raiseAlert'
    ];

    /**
     * TestAPI Results Report Controller
     * This controller is for the '/results/<test run ID>' page where a user can
     * view details for a specific test run.
     */
    function ResultsReportController($http, $stateParams, $window,
        $uibModal, testapiApiUrl, raiseAlert) {

        var ctrl = this;

        ctrl.getResults = getResults;
        ctrl.gotoDoc = gotoDoc;
        ctrl.openAll = openAll;
        ctrl.folderAll = folderAll;

        /** The testID extracted from the URL route. */
        ctrl.testId = $stateParams.testID;

        /** The HTML template that all accordian groups will use. */
        ctrl.detailsTemplate = 'testapi-ui/components/results-report/partials/' +
                               'reportDetails.html';

        ctrl.total = 0;
        ctrl.mandatory_total = 0;
        ctrl.mandatory_pass = 0;
        ctrl.mandatory_fail = 0;
        ctrl.optional_total = 0;
        ctrl.optional_pass = 0;
        ctrl.optional_fail = 0;

        ctrl.testStatus = 'total';


        /**
         * Retrieve results from the TestAPI API server based on the test
         * run id in the URL. This function is the first function that will
         * be called from the controller. Upon successful retrieval of results,
         * the function that gets the version list will be called.
         */
        function getResults() {
            ctrl.cases = [];
            $http.get(testapiApiUrl + '/projects/dovetail/cases').success(function(case_name_data){
                var case_name_list = case_name_data.testcases;
                angular.forEach(case_name_list, function(ele){
                    var content_url = testapiApiUrl + '/results?build_tag=' + 'daily-master-' + ctrl.testId + '-' + ele.name;
                    ctrl.resultsRequest =
                        $http.get(content_url).success(function(data) {
                            var result_cases = data.results;
                            angular.forEach(result_cases, function(result_case){
                                if(result_case.project_name == 'yardstick'){
                                    yardstickHandler(result_case);
                                }else{
                                    functestHandler(result_case);
                                }
                            });
                        }).error(function (error) {
                            ctrl.showError = true;
                            ctrl.resultsData = null;
                            ctrl.error = 'Error retrieving results from server: ' +
                                angular.toJson(error);
                        });
                    });
            });
        }

        function functestHandler(result_case){
            result_case.total = 0;
            result_case.pass = 0;
            result_case.fail = 0;
            if(result_case.details.success){
                var sub_cases = result_case.details.success.split(',');
                sub_cases.pop();
                result_case.details.success = sub_cases;
                result_case.total += sub_cases.length;
                result_case.pass += sub_cases.length;
            }
            if(result_case.details.errors){
                var sub_cases = result_case.details.errors.split(',');
                sub_cases.pop();
                result_case.details.errors = sub_cases;
                result_case.total += sub_cases.length;
                result_case.fail += sub_cases.length;
            }
            if(result_case.total == 0){
                result_case.total = 1;
                if(result_case.criteria == 'PASS'){
                    result_case.pass = 1;
                }else{
                    result_case.fail = 1;
                }
            }
            result_case.folder = true;
            ctrl.cases.push(result_case);
            count(result_case);
        }

        function yardstickHandler(result_case){
            result_case.total = 0;
            result_case.pass = 0;
            result_case.fail = 0;
            angular.forEach(result_case.details.results, function(ele){
                if(ele.benchmark){
                    result_case.total = 1;
                    if(ele.benchmark.data.sla_pass == 1){
                        result_case.criteria = 'PASS';
                        result_case.pass = 1;
                    }else{
                        result_case.criteria = 'FAILED';
                        result_case.fail = 1;
                    }
                    return false;
                }
            });
            result_case.folder = true;
            ctrl.cases.push(result_case);
            count(result_case);
        }

        function count(result_case){
            var build_tag = result_case.build_tag;
            var tag = build_tag.split('-').pop().split('.')[1];
            ctrl.total += result_case.total;
            if(tag == 'ha' || tag == 'defcore' || tag == 'vping'){
                ctrl.mandatory_total += result_case.total;
                ctrl.mandatory_pass += result_case.pass;
                ctrl.mandatory_fail += result_case.fail;
            }else{
                ctrl.optional_total += result_case.total;
                ctrl.optional_pass += result_case.pass;
                ctrl.optional_fail += result_case.fail;
            }
        }

        function gotoDoc(sub_case){
        }

        function openAll(){
            angular.forEach(ctrl.cases, function(ele){
                ele.folder = false;
            });
        }

        function folderAll(){
            angular.forEach(ctrl.cases, function(ele){
                ele.folder = true;
            });
        }

        getResults();
    }

})();
